import pandas as pd


def apply_action_governance(
    action_register,
    created_date=None,
    target_days=7
):
    """
    Apply operational governance fields to a FinOps action register.

    Adds:
        Created_Date
        Target_Date
        Completed_Date
        Days_Open
        SLA_Status
    """

    governed = action_register.copy()

    # ----------------------------------------
    # Handle empty action register
    # ----------------------------------------

    if governed.empty:

        governed["Created_Date"] = pd.Series(
            dtype="datetime64[ns]"
        )

        governed["Target_Date"] = pd.Series(
            dtype="datetime64[ns]"
        )

        governed["Completed_Date"] = pd.Series(
            dtype="datetime64[ns]"
        )

        governed["Days_Open"] = pd.Series(
            dtype="int64"
        )

        governed["SLA_Status"] = pd.Series(
            dtype="object"
        )

        return governed

    # ----------------------------------------
    # Created date
    # ----------------------------------------

    if created_date is None:

        created = pd.Timestamp.today().normalize()

    else:

        created = pd.Timestamp(created_date)

    governed["Created_Date"] = created

    # ----------------------------------------
    # Target date
    # ----------------------------------------

    governed["Target_Date"] = (
        governed["Created_Date"]
        + pd.to_timedelta(
            target_days,
            unit="D"
        )
    )

    # ----------------------------------------
    # Completed date
    # ----------------------------------------

    if "Completed_Date" not in governed.columns:

        governed["Completed_Date"] = pd.NaT

    else:

        governed["Completed_Date"] = pd.to_datetime(
            governed["Completed_Date"],
            errors="coerce"
        )

    # ----------------------------------------
    # Days open
    # ----------------------------------------

    today = pd.Timestamp.today().normalize()

    governed["Days_Open"] = (
        governed["Completed_Date"]
        .fillna(today)
        .sub(governed["Created_Date"])
        .dt.days
    )

    # ----------------------------------------
    # SLA status
    # ----------------------------------------

    def determine_sla_status(row):

        completed_date = row["Completed_Date"]
        target_date = row["Target_Date"]

        # Completed actions
        if pd.notna(completed_date):

            if completed_date <= target_date:
                return "COMPLETED_ON_TIME"

            return "COMPLETED_LATE"

        # Open actions
        if today <= target_date:
            return "ON_TRACK"

        return "OVERDUE"

    governed["SLA_Status"] = governed.apply(
        determine_sla_status,
        axis=1
    )

    return governed
