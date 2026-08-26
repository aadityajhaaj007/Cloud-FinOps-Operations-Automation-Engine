import pandas as pd


def calculate_governance_intelligence(
    action_register,
    at_risk_days=2
):
    """
    Calculate operational governance KPIs for the FinOps action register.

    Parameters
    ----------
    action_register : pandas.DataFrame
        Governed FinOps action register containing SLA fields.

    at_risk_days : int
        Number of days before the target date at which an open
        action should be considered at risk.

    Returns
    -------
    dict
        Governance KPI summary.
    """

    if action_register is None:
        action_register = pd.DataFrame()

    if action_register.empty:

        return {
            "total_actions": 0,
            "open_actions": 0,
            "completed_actions": 0,
            "on_track_actions": 0,
            "at_risk_actions": 0,
            "overdue_actions": 0,
            "escalated_actions": 0,
            "high_priority_actions": 0,
            "medium_priority_actions": 0,
            "total_estimated_savings": 0.0,
            "open_savings_exposure": 0.0,
            "overdue_savings_exposure": 0.0,
            "sla_compliance_percentage": 100.0
        }

    governed = action_register.copy()

    total_actions = len(governed)

    # ----------------------------------------
    # Normalize required fields
    # ----------------------------------------

    if "Action_Status" not in governed.columns:
        governed["Action_Status"] = "OPEN"

    if "Priority" not in governed.columns:
        governed["Priority"] = "MEDIUM"

    if "Estimated_Savings" not in governed.columns:
        governed["Estimated_Savings"] = 0.0

    governed["Estimated_Savings"] = pd.to_numeric(
        governed["Estimated_Savings"],
        errors="coerce"
    ).fillna(0.0)

    # ----------------------------------------
    # SLA status
    # ----------------------------------------

    if "SLA_Status" in governed.columns:

        sla_status = (
            governed["SLA_Status"]
            .fillna("ON_TRACK")
            .astype(str)
            .str.upper()
        )

    else:

        sla_status = pd.Series(
            ["ON_TRACK"] * total_actions,
            index=governed.index
        )

    # ----------------------------------------
    # Action status
    # ----------------------------------------

    action_status = (
        governed["Action_Status"]
        .fillna("OPEN")
        .astype(str)
        .str.upper()
    )

    open_mask = action_status == "OPEN"

    completed_mask = (
        action_status == "COMPLETED"
    )

    # ----------------------------------------
    # SLA categories
    # ----------------------------------------

    on_track_mask = sla_status == "ON_TRACK"

    at_risk_mask = sla_status == "AT_RISK"

    overdue_mask = sla_status == "OVERDUE"

    escalated_mask = sla_status == "ESCALATED"

    # ----------------------------------------
    # Priority
    # ----------------------------------------

    priority = (
        governed["Priority"]
        .fillna("MEDIUM")
        .astype(str)
        .str.upper()
    )

    high_priority_mask = priority == "HIGH"

    medium_priority_mask = priority == "MEDIUM"

    # ----------------------------------------
    # Savings
    # ----------------------------------------

    total_estimated_savings = (
        governed["Estimated_Savings"].sum()
    )

    open_savings_exposure = (
        governed.loc[
            open_mask,
            "Estimated_Savings"
        ].sum()
    )

    overdue_savings_exposure = (
        governed.loc[
            overdue_mask,
            "Estimated_Savings"
        ].sum()
    )

    # ----------------------------------------
    # SLA compliance
    # ----------------------------------------

    applicable_actions = total_actions

    compliant_actions = (
        on_track_mask
        | completed_mask
        & ~overdue_mask
    ).sum()

    if applicable_actions > 0:

        sla_compliance_percentage = (
            compliant_actions
            / applicable_actions
            * 100
        )

    else:

        sla_compliance_percentage = 100.0

    # ----------------------------------------
    # Result
    # ----------------------------------------

    return {
        "total_actions": int(total_actions),
        "open_actions": int(open_mask.sum()),
        "completed_actions": int(completed_mask.sum()),
        "on_track_actions": int(on_track_mask.sum()),
        "at_risk_actions": int(at_risk_mask.sum()),
        "overdue_actions": int(overdue_mask.sum()),
        "escalated_actions": int(escalated_mask.sum()),
        "high_priority_actions": int(
            high_priority_mask.sum()
        ),
        "medium_priority_actions": int(
            medium_priority_mask.sum()
        ),
        "total_estimated_savings": float(
            total_estimated_savings
        ),
        "open_savings_exposure": float(
            open_savings_exposure
        ),
        "overdue_savings_exposure": float(
            overdue_savings_exposure
        ),
        "sla_compliance_percentage": round(
            float(sla_compliance_percentage),
            2
        )
    }