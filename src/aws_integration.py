import pandas as pd


REQUIRED_AWS_COLUMNS = [
    "Date",
    "Resource_ID",
    "Service",
    "Region",
    "Business_Unit",
    "Environment",
    "CPU_Utilization",
    "Storage_GB",
    "Monthly_Cost",
    "Owner",
    "Resource_Status"
]


class MockAWSProvider:
    """
    Mock AWS data provider for local development and CI testing.

    Returns a normalized DataFrame using the same schema
    expected by the existing FinOps pipeline.
    """

    def __init__(self, data=None):
        self.data = data

    def get_cost_data(self):
        """
        Return mock AWS cost/resource data as a DataFrame.
        """

        if self.data is None:
            return pd.DataFrame(columns=REQUIRED_AWS_COLUMNS)

        df = pd.DataFrame(self.data)

        return normalize_aws_data(df)


class AWSProvider:
    """
    AWS data provider.

    Real AWS API integrations will be added incrementally
    in later v1.7 releases.
    """

    def __init__(self, region_name=None):
        self.region_name = region_name

    def get_cost_data(self):
        """
        Placeholder for AWS Cost Explorer integration.
        """

        raise NotImplementedError(
            "AWS Cost Explorer integration is not implemented yet."
        )


def normalize_aws_data(df):
    """
    Normalize AWS/provider data into the schema expected
    by the FinOps pipeline.
    """

    missing_columns = [
        column
        for column in REQUIRED_AWS_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing AWS data columns: {missing_columns}"
        )

    normalized = df[REQUIRED_AWS_COLUMNS].copy()

    normalized["Date"] = pd.to_datetime(
        normalized["Date"],
        errors="coerce"
    )

    normalized["CPU_Utilization"] = pd.to_numeric(
        normalized["CPU_Utilization"],
        errors="coerce"
    )

    normalized["Storage_GB"] = pd.to_numeric(
        normalized["Storage_GB"],
        errors="coerce"
    )

    normalized["Monthly_Cost"] = pd.to_numeric(
        normalized["Monthly_Cost"],
        errors="coerce"
    )

    return normalized


def get_cost_data(provider):
    """
    Retrieve and normalize data from the selected provider.
    """

    if provider is None:
        raise ValueError(
            "An AWS data provider must be supplied."
        )

    df = provider.get_cost_data()

    return normalize_aws_data(df)