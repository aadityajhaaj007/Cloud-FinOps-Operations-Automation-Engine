import pandas as pd

from src.optimization_engine import (
    generate_optimization_candidates
)


def calculate_savings_intelligence(
    df,
    cpu_threshold=30,
    savings_assumption=0.30
):
    """
    Calculate FinOps savings intelligence.
    """

    candidates = generate_optimization_candidates(
        df,
        cpu_threshold,
        savings_assumption
    )

    rightsizing = candidates[
        candidates["Opportunity_Type"] == "Rightsizing"
    ].copy()

    total_spend = float(
        df["Monthly_Cost"].sum()
    )

    optimization_exposure = float(
        candidates["Monthly_Cost"].sum()
    )

    rightsizing_exposure = float(
        rightsizing["Monthly_Cost"].sum()
    )

    estimated_savings = float(
        rightsizing["Estimated_Savings"].sum()
    )

    savings_percentage = 0.0

    if total_spend > 0:
        savings_percentage = (
            estimated_savings
            / total_spend
            * 100
        )

    # ========================================
    # SERVICE SAVINGS
    # ========================================

    if not rightsizing.empty:

        service_savings = (
            rightsizing
            .groupby("Service")
            .agg(
                resource_count=(
                    "Resource_ID",
                    "count"
                ),
                cost_exposure=(
                    "Monthly_Cost",
                    "sum"
                ),
                estimated_savings=(
                    "Estimated_Savings",
                    "sum"
                )
            )
            .sort_values(
                "estimated_savings",
                ascending=False
            )
        )

    else:

        service_savings = pd.DataFrame(
            columns=[
                "resource_count",
                "cost_exposure",
                "estimated_savings"
            ]
        )

    # ========================================
    # BUSINESS UNIT SAVINGS
    # ========================================

    if not rightsizing.empty:

        business_unit_savings = (
            rightsizing
            .groupby("Business_Unit")
            .agg(
                resource_count=(
                    "Resource_ID",
                    "count"
                ),
                cost_exposure=(
                    "Monthly_Cost",
                    "sum"
                ),
                estimated_savings=(
                    "Estimated_Savings",
                    "sum"
                )
            )
            .sort_values(
                "estimated_savings",
                ascending=False
            )
        )

    else:

        business_unit_savings = pd.DataFrame(
            columns=[
                "resource_count",
                "cost_exposure",
                "estimated_savings"
            ]
        )

    # ========================================
    # TOP SAVINGS OPPORTUNITIES
    # ========================================

    top_opportunities = (
        rightsizing[
            [
                "Resource_ID",
                "Service",
                "Business_Unit",
                "Resource_Status",
                "CPU_Utilization",
                "Monthly_Cost",
                "Estimated_Savings",
                "Priority",
                "Recommendation"
            ]
        ]
        .sort_values(
            "Estimated_Savings",
            ascending=False
        )
        .reset_index(drop=True)
    )

    if not top_opportunities.empty:

        top_opportunities.insert(
            0,
            "Savings_Rank",
            range(
                1,
                len(top_opportunities) + 1
            )
        )

    return {
        "total_spend": total_spend,
        "optimization_exposure": optimization_exposure,
        "rightsizing_exposure": rightsizing_exposure,
        "estimated_savings": estimated_savings,
        "savings_percentage": savings_percentage,
        "rightsizing_count": int(
            len(rightsizing)
        ),
        "service_savings": service_savings,
        "business_unit_savings": (
            business_unit_savings
        ),
        "top_opportunities": top_opportunities
    }
