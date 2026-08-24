from src.optimization_engine import (
    generate_optimization_candidates
)


def calculate_total_spend(df):
    return df["Monthly_Cost"].sum()


def calculate_cost_by_service(df):
    return (
        df.groupby("Service")["Monthly_Cost"]
        .sum()
        .sort_values(ascending=False)
    )


def calculate_cost_by_business_unit(df):
    return (
        df.groupby("Business_Unit")["Monthly_Cost"]
        .sum()
        .sort_values(ascending=False)
    )


def calculate_cost_by_resource_status(df):
    return (
        df.groupby("Resource_Status")["Monthly_Cost"]
        .sum()
        .sort_values(ascending=False)
    )


def calculate_resource_status_summary(df):

    return (
        df.groupby("Resource_Status")
        .agg(
            resource_count=("Resource_ID", "count"),
            total_cost=("Monthly_Cost", "sum")
        )
        .sort_values(
            "total_cost",
            ascending=False
        )
    )


def calculate_average_cpu(df):

    return df["CPU_Utilization"].mean()


def calculate_low_utilization_resources(
    df,
    cpu_threshold=30
):

    return df[
        (df["Resource_Status"] == "Running")
        &
        (df["CPU_Utilization"] < cpu_threshold)
    ].copy()


def calculate_optimization_summary(
    df,
    cpu_threshold=30,
    savings_assumption=0.30
):

    # Use the central optimization engine
    candidates = generate_optimization_candidates(
        df,
        cpu_threshold,
        savings_assumption
    )

    # ----------------------------------------
    # Rightsizing opportunities
    # ----------------------------------------

    rightsizing = candidates[
        candidates["Opportunity_Type"]
        == "Rightsizing"
    ]

    rightsizing_candidates = len(
        rightsizing
    )

    rightsizing_cost_exposure = float(
        rightsizing["Monthly_Cost"].sum()
    )

    estimated_rightsizing_savings = float(
        rightsizing["Estimated_Savings"].sum()
    )

    # ----------------------------------------
    # Stopped resource investigations
    # ----------------------------------------

    stopped_investigations = candidates[
        candidates["Opportunity_Type"]
        == "Stopped Resource Investigation"
    ]

    stopped_resource_count = len(
        stopped_investigations
    )

    stopped_cost_exposure = float(
        stopped_investigations[
            "Monthly_Cost"
        ].sum()
    )

    # ----------------------------------------
    # Priority counts
    # ----------------------------------------

    high_priority_count = int(
        (candidates["Priority"] == "HIGH")
        .sum()
    )

    medium_priority_count = int(
        (candidates["Priority"] == "MEDIUM")
        .sum()
    )

    # ----------------------------------------
    # Total optimization candidates
    # ----------------------------------------

    total_candidates = len(candidates)

    total_spend = float(
        df["Monthly_Cost"].sum()
    )

    # ----------------------------------------
    # Estimated savings percentage
    #
    # Only rightsizing savings are treated
    # as estimated savings opportunity.
    # ----------------------------------------

    estimated_savings_percentage = 0.0

    if total_spend > 0:

        estimated_savings_percentage = (
            estimated_rightsizing_savings
            / total_spend
            * 100
        )

    return {

        "optimization_candidates": int(
            total_candidates
        ),

        "rightsizing_candidates": int(
            rightsizing_candidates
        ),

        "rightsizing_cost_exposure": (
            rightsizing_cost_exposure
        ),

        "estimated_rightsizing_savings": (
            estimated_rightsizing_savings
        ),

        "estimated_savings_percentage": float(
            estimated_savings_percentage
        ),

        "stopped_resource_investigations": int(
            stopped_resource_count
        ),

        "stopped_cost_exposure": (
            stopped_cost_exposure
        ),

        "high_priority_opportunities": (
            high_priority_count
        ),

        "medium_priority_opportunities": (
            medium_priority_count
        )
    }


def generate_kpi_summary(
    df,
    cpu_threshold=30,
    savings_assumption=0.30
):

    optimization = calculate_optimization_summary(
        df,
        cpu_threshold,
        savings_assumption
    )

    running_resources = df[
        df["Resource_Status"] == "Running"
    ]

    stopped_resources = df[
        df["Resource_Status"] == "Stopped"
    ]

    return {

        # ------------------------------------
        # Overall financial metrics
        # ------------------------------------

        "total_spend": float(
            calculate_total_spend(df)
        ),

        "resource_count": int(
            len(df)
        ),

        "average_resource_cost": float(
            df["Monthly_Cost"].mean()
        ),

        # ------------------------------------
        # Resource state
        # ------------------------------------

        "running_resources": int(
            len(running_resources)
        ),

        "stopped_resources": int(
            len(stopped_resources)
        ),

        "running_cost": float(
            running_resources[
                "Monthly_Cost"
            ].sum()
        ),

        "stopped_cost": float(
            stopped_resources[
                "Monthly_Cost"
            ].sum()
        ),

        # ------------------------------------
        # Organizational dimensions
        # ------------------------------------

        "service_count": int(
            df["Service"].nunique()
        ),

        "business_unit_count": int(
            df["Business_Unit"].nunique()
        ),

        # ------------------------------------
        # Utilization
        # ------------------------------------

        "average_cpu_utilization": float(
            calculate_average_cpu(df)
        ),

        # ------------------------------------
        # Optimization
        # ------------------------------------

        "optimization_candidates": int(
            optimization[
                "optimization_candidates"
            ]
        ),

        "rightsizing_candidates": int(
            optimization[
                "rightsizing_candidates"
            ]
        ),

        "rightsizing_cost_exposure": float(
            optimization[
                "rightsizing_cost_exposure"
            ]
        ),

       "estimated_rightsizing_savings": round(
    float(
        optimization[
            "estimated_rightsizing_savings"
        ]
    ),
    2
),

        "estimated_savings_percentage": round(
    float(
        optimization[
            "estimated_savings_percentage"
        ]
    ),
    2
),

        # ------------------------------------
        # Stopped resources
        # ------------------------------------

        "stopped_resource_investigations": int(
            optimization[
                "stopped_resource_investigations"
            ]
        ),

        "stopped_cost_exposure": float(
            optimization[
                "stopped_cost_exposure"
            ]
        ),

        # ------------------------------------
        # Priority
        # ------------------------------------

        "high_priority_opportunities": int(
            optimization[
                "high_priority_opportunities"
            ]
        ),

        "medium_priority_opportunities": int(
            optimization[
                "medium_priority_opportunities"
            ]
        )
    }