def get_service_recommendation(service):

    recommendations = {

        "EC2": (
            "Review EC2 instance utilization "
            "and consider instance rightsizing"
        ),

        "RDS": (
            "Review database instance utilization "
            "and consider DB instance rightsizing"
        ),

        "EBS": (
            "Review EBS volume utilization, "
            "size, and attachment status"
        ),

        "S3": (
            "Review S3 storage usage, "
            "storage class, and lifecycle configuration"
        ),

        "Lambda": (
            "Review Lambda memory allocation "
            "and invocation utilization"
        ),

        "CloudFront": (
            "Review CloudFront distribution usage "
            "and configuration"
        )
    }

    return recommendations.get(
        service,
        "Review resource utilization and configuration"
    )


def generate_recommendation(
    row,
    cpu_threshold
):

    cpu = row["CPU_Utilization"]
    status = row["Resource_Status"]
    cost = row["Monthly_Cost"]
    service = row["Service"]

    # ========================================
    # 1. Stopped resource
    # ========================================

    if status == "Stopped":

        if cost >= 20000:

            return (
                "Stopped Resource Investigation",

                "Resource is stopped and has "
                "significant monthly cost exposure",

                "Validate service-specific state "
                "and investigate whether the resource "
                "can be retired, released, or otherwise "
                "optimized",

                "HIGH"
            )

        return (
            "Stopped Resource Investigation",

            "Resource is currently stopped",

            "Validate service-specific state "
            "before taking action",

            "MEDIUM"
        )

    # ========================================
    # 2. High-priority rightsizing
    # ========================================

    if cpu < 20 and cost >= 20000:

        return (
            "Rightsizing",

            "Very low CPU utilization on a "
            "high-cost running resource",

            get_service_recommendation(
                service
            ),

            "HIGH"
        )

    # ========================================
    # 3. Medium-priority rightsizing
    # ========================================

    if cpu < cpu_threshold:

        return (
            "Rightsizing",

            "Low CPU utilization on a "
            "running resource",

            get_service_recommendation(
                service
            ),

            "MEDIUM"
        )

    # ========================================
    # 4. No optimization signal
    # ========================================

    return (
        "No Immediate Action",

        "No significant optimization "
        "signal detected",

        "No immediate optimization action",

        "LOW"
    )


def generate_optimization_candidates(
    df,
    cpu_threshold,
    savings_assumption
):

    # ========================================
    # Candidate identification
    # ========================================

    candidates = df[
        (
            df["CPU_Utilization"]
            < cpu_threshold
        )
        |
        (
            df["Resource_Status"]
            == "Stopped"
        )
    ].copy()

    # ========================================
    # Generate recommendations
    # ========================================

    recommendations = candidates.apply(
        lambda row: generate_recommendation(
            row,
            cpu_threshold
        ),
        axis=1
    )

    # ========================================
    # Add opportunity type
    # ========================================

    candidates["Opportunity_Type"] = (
        recommendations.apply(
            lambda value: value[0]
        )
    )

    # ========================================
    # Add reason
    # ========================================

    candidates["Reason"] = (
        recommendations.apply(
            lambda value: value[1]
        )
    )

    # ========================================
    # Add recommendation
    # ========================================

    candidates["Recommendation"] = (
        recommendations.apply(
            lambda value: value[2]
        )
    )

    # ========================================
    # Add priority
    # ========================================

    candidates["Priority"] = (
        recommendations.apply(
            lambda value: value[3]
        )
    )

    # ========================================
    # Estimated savings opportunity
    #
    # Only Rightsizing candidates receive
    # an estimated savings value.
    #
    # Stopped resources are treated as
    # cost exposure, NOT guaranteed savings.
    # ========================================

    candidates["Estimated_Savings"] = 0.0

    rightsizing_mask = (
        candidates["Opportunity_Type"]
        == "Rightsizing"
    )

    candidates.loc[
        rightsizing_mask,
        "Estimated_Savings"
    ] = (
        candidates.loc[
            rightsizing_mask,
            "Monthly_Cost"
        ]
        * savings_assumption
    )

    # ========================================
    # Priority ranking
    # ========================================

    priority_order = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    candidates["Priority_Rank"] = (
        candidates["Priority"]
        .map(priority_order)
    )

    # ========================================
    # Sort candidates
    #
    # HIGH first
    # MEDIUM second
    # LOW last
    #
    # Within each priority, highest
    # estimated savings comes first.
    # ========================================

    candidates = candidates.sort_values(
        by=[
            "Priority_Rank",
            "Estimated_Savings"
        ],
        ascending=[
            True,
            False
        ]
    )

    # ========================================
    # Final optimization rank
    # ========================================

    candidates["Optimization_Rank"] = range(
        1,
        len(candidates) + 1
    )

    # ========================================
    # Remove internal ranking column
    # ========================================

    candidates = candidates.drop(
        columns=[
            "Priority_Rank"
        ]
    )

    return candidates