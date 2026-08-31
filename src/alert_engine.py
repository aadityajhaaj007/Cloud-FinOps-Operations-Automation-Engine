import pandas as pd


def generate_operational_alerts(
    action_register,
    high_value_threshold=5000.0
):
    """
    Generate operational FinOps alerts from the governed
    savings action register.

    Parameters
    ----------
    action_register : pandas.DataFrame
        Governed FinOps action register.

    high_value_threshold : float
        Estimated savings threshold for high-value alerts.

    Returns
    -------
    pandas.DataFrame
        Operational alert register.
    """

    alert_columns = [
        "Alert_ID",
        "Alert_Type",
        "Severity",
        "Action_ID",
        "Resource_ID",
        "Owner",
        "Priority",
        "Estimated_Savings",
        "Message",
        "Alert_Status",
        "Created_Date"
    ]

    # ----------------------------------------
    # Empty register handling
    # ----------------------------------------

    if action_register is None or action_register.empty:
        return pd.DataFrame(columns=alert_columns)

    governed = action_register.copy()

    # ----------------------------------------
    # Required field defaults
    # ----------------------------------------

    defaults = {
        "Action_ID": "",
        "Resource_ID": "",
        "Owner": "",
        "Priority": "MEDIUM",
        "Estimated_Savings": 0.0,
        "Action_Status": "OPEN",
        "SLA_Status": "ON_TRACK",
        "Created_Date": ""
    }

    for column, default in defaults.items():

        if column not in governed.columns:
            governed[column] = default

    # ----------------------------------------
    # Normalize fields
    # ----------------------------------------

    governed["Priority"] = (
        governed["Priority"]
        .fillna("MEDIUM")
        .astype(str)
        .str.upper()
    )

    governed["Action_Status"] = (
        governed["Action_Status"]
        .fillna("OPEN")
        .astype(str)
        .str.upper()
    )

    governed["SLA_Status"] = (
        governed["SLA_Status"]
        .fillna("ON_TRACK")
        .astype(str)
        .str.upper()
    )

    governed["Estimated_Savings"] = pd.to_numeric(
        governed["Estimated_Savings"],
        errors="coerce"
    ).fillna(0.0)

    # ----------------------------------------
    # Generate alerts
    # ----------------------------------------

    alerts = []

    alert_counter = 1

    for _, row in governed.iterrows():

        action_id = row["Action_ID"]
        resource_id = row["Resource_ID"]
        owner = row["Owner"]
        priority = row["Priority"]
        savings = float(row["Estimated_Savings"])
        action_status = row["Action_Status"]
        sla_status = row["SLA_Status"]
        created_date = row["Created_Date"]

        # ----------------------------------------
        # 1. Overdue action
        # ----------------------------------------

        if (
            action_status == "OPEN"
            and sla_status == "OVERDUE"
        ):

            alerts.append({
                "Alert_ID": f"ALT-{alert_counter:04d}",
                "Alert_Type": "OVERDUE_ACTION",
                "Severity": "CRITICAL",
                "Action_ID": action_id,
                "Resource_ID": resource_id,
                "Owner": owner,
                "Priority": priority,
                "Estimated_Savings": savings,
                "Message": (
                    f"Action {action_id} is overdue "
                    f"and requires immediate attention."
                ),
                "Alert_Status": "OPEN",
                "Created_Date": created_date
            })

            alert_counter += 1

        # ----------------------------------------
        # 2. At-risk action
        # ----------------------------------------

        elif (
            action_status == "OPEN"
            and sla_status == "AT_RISK"
        ):

            alerts.append({
                "Alert_ID": f"ALT-{alert_counter:04d}",
                "Alert_Type": "AT_RISK_ACTION",
                "Severity": "HIGH",
                "Action_ID": action_id,
                "Resource_ID": resource_id,
                "Owner": owner,
                "Priority": priority,
                "Estimated_Savings": savings,
                "Message": (
                    f"Action {action_id} is approaching "
                    f"its SLA target."
                ),
                "Alert_Status": "OPEN",
                "Created_Date": created_date
            })

            alert_counter += 1

        # ----------------------------------------
        # 3. Escalated action
        # ----------------------------------------

        if (
            action_status == "OPEN"
            and sla_status == "ESCALATED"
        ):

            alerts.append({
                "Alert_ID": f"ALT-{alert_counter:04d}",
                "Alert_Type": "ESCALATED_ACTION",
                "Severity": "CRITICAL",
                "Action_ID": action_id,
                "Resource_ID": resource_id,
                "Owner": owner,
                "Priority": priority,
                "Estimated_Savings": savings,
                "Message": (
                    f"Action {action_id} has been escalated "
                    f"for management attention."
                ),
                "Alert_Status": "OPEN",
                "Created_Date": created_date
            })

            alert_counter += 1

        # ----------------------------------------
        # 4. High-value savings
        # ----------------------------------------

        if (
            action_status == "OPEN"
            and savings >= high_value_threshold
        ):

            alerts.append({
                "Alert_ID": f"ALT-{alert_counter:04d}",
                "Alert_Type": "HIGH_VALUE_SAVINGS",
                "Severity": (
                    "HIGH"
                    if priority == "HIGH"
                    else "MEDIUM"
                ),
                "Action_ID": action_id,
                "Resource_ID": resource_id,
                "Owner": owner,
                "Priority": priority,
                "Estimated_Savings": savings,
                "Message": (
                    f"Action {action_id} represents "
                    f"₹{savings:,.2f} in estimated savings."
                ),
                "Alert_Status": "OPEN",
                "Created_Date": created_date
            })

            alert_counter += 1

    # ----------------------------------------
    # Return alert register
    # ----------------------------------------

    return pd.DataFrame(
        alerts,
        columns=alert_columns
    )