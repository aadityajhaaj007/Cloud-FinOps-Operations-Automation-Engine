from datetime import datetime, timedelta

import boto3
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

AWS_SERVICE_MAP = {
    "Amazon Elastic Compute Cloud - Compute": "EC2",
    "Amazon Simple Storage Service": "S3",
    "Amazon Relational Database Service": "RDS",
    "AWS Lambda": "Lambda",
    "Amazon CloudFront": "CloudFront",
    "Amazon Elastic Block Store": "EBS",
}


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
    AWS data provider using AWS Cost Explorer.

    Cost Explorer provides aggregated AWS cost data.
    Resource-level enrichment will be added in later
    v1.7 releases.
    """

    def __init__(self, region_name=None):
        self.region_name = region_name

        self.cost_explorer = boto3.client(
            "ce",
            region_name=region_name
        )

    def get_cost_data(
        self,
        start_date=None,
        end_date=None
    ):
        """
        Retrieve AWS cost data from Cost Explorer.

        If dates are not supplied, retrieve the previous
        30 days of cost data.
        """

        if start_date is None:
            start_date = (
                datetime.utcnow() - timedelta(days=30)
            ).strftime("%Y-%m-%d")

        if end_date is None:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")

        request_parameters = {
            "TimePeriod": {
                "Start": start_date,
                "End": end_date
            },
            "Granularity": "DAILY",
            "Metrics": ["UnblendedCost"],
            "GroupBy": [
                {
                    "Type": "DIMENSION",
                    "Key": "SERVICE"
                }
            ]
        }

        all_results = []

        while True:

            response = self.cost_explorer.get_cost_and_usage(
                **request_parameters
            )

            all_results.extend(
                response.get("ResultsByTime", [])
            )

            next_page_token = response.get(
                "NextPageToken"
            )

            if not next_page_token:
                break

            request_parameters["NextPageToken"] = (
                next_page_token
            )

        combined_response = {
            "ResultsByTime": all_results
        }

        return self._parse_cost_response(
            combined_response
        )

    def _parse_cost_response(self, response):
        """
        Convert Cost Explorer response into a DataFrame.
        """

        records = []

        for result in response.get("ResultsByTime", []):

            date = result["TimePeriod"]["Start"]

            for group in result.get("Groups", []):

                aws_service = group["Keys"][0]

                service = AWS_SERVICE_MAP.get(
                    aws_service,
                    aws_service
                )

                amount = float(
                    group["Metrics"]["UnblendedCost"]["Amount"]
                )

                records.append(
                    {
                        "Date": date,
                        "Resource_ID": "AWS-COST-AGGREGATE",
                        "Service": service,
                        "Region": self.region_name or "global",
                        "Business_Unit": "Unknown",
                        "Environment": "Unknown",
                        "CPU_Utilization": 0,
                        "Storage_GB": 0,
                        "Monthly_Cost": amount,
                        "Owner": "Unknown",
                        "Resource_Status": "Running"
                    }
                )

        df = pd.DataFrame(
            records,
            columns=REQUIRED_AWS_COLUMNS
        )

        return normalize_aws_data(df)

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