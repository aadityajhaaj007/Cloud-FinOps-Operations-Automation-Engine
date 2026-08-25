import pandas as pd


def generate_action_register(
    df,
    savings_intelligence
):
    """
    Convert savings opportunities into an operational
    FinOps action register.

    The register preserves the savings intelligence ranking
    and adds operational tracking fields.
    """

    if savings_intelligence is None:
        return pd.DataFrame(
            columns=[
                "Action_ID",
                "Savings_Rank",
                "Resource_ID",
                "Service",
                "Business_Unit",
                "Owner",
                "Priority",
                "Resource_Status",
                "CPU_Utilization",
                "Monthly_Cost",
                "Estimated_Savings",
                "Recommendation",
                "Action_Status",
                "Target_Date",
                "Notes"
            ]
        )

    opportunities = savings_intelligence.get(
        "top_opportunities"
    )

    if opportunities is None or opportunities.empty:
        return pd.DataFrame(
            columns=[
                "Action_ID",
                "Savings_Rank",
                "Resource_ID",
                "Service",
                "Business_Unit",
                "Owner",
                "Priority",
                "Resource_Status",
                "CPU_Utilization",
                "Monthly_Cost",
                "Estimated_Savings",
                "Recommendation",
                "Action_Status",
                "Target_Date",
                "Notes"
            ]
        )

    register = opportunities.copy()

    # ------------------------------------------------
    # Add source owner information
    # ------------------------------------------------

    owner_map = (
        df[
            [
                "Resource_ID",
                "Owner"
            ]
        ]
        .drop_duplicates(
            subset=["Resource_ID"]
        )
    )

    register = register.merge(
        owner_map,
        on="Resource_ID",
        how="left"
    )

    # ------------------------------------------------
    # Generate stable action IDs
    # ------------------------------------------------

    register.insert(
        0,
        "Action_ID",
        [
            f"FIN-{rank:04d}"
            for rank in register["Savings_Rank"]
        ]
    )

    # ------------------------------------------------
    # Operational workflow fields
    # ------------------------------------------------

    register["Action_Status"] = "OPEN"

    register["Target_Date"] = ""

    register["Notes"] = ""

    # ------------------------------------------------
    # Arrange columns
    # ------------------------------------------------

    register = register[
        [
            "Action_ID",
            "Savings_Rank",
            "Resource_ID",
            "Service",
            "Business_Unit",
            "Owner",
            "Priority",
            "Resource_Status",
            "CPU_Utilization",
            "Monthly_Cost",
            "Estimated_Savings",
            "Recommendation",
            "Action_Status",
            "Target_Date",
            "Notes"
        ]
    ]

    return register
