import pandas as pd


RESOURCE_INVENTORY_COLUMNS = [
    "Resource_ID",
    "Service",
    "Region",
    "Business_Unit",
    "Environment",
    "Owner",
    "Resource_Status"
]


SUPPORTED_RESOURCE_SERVICES = [
    "EC2",
    "S3",
    "RDS"
]


def validate_resource_inventory_schema(df):
    """
    Validate that the resource inventory contains
    the required standardized columns.
    """

    missing_columns = [
        column
        for column in RESOURCE_INVENTORY_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing resource inventory columns: {missing_columns}"
        )

    return True


def validate_resource_inventory_services(df):
    """
    Validate that all resource services are supported.
    """

    invalid_services = df[
        ~df["Service"].isin(SUPPORTED_RESOURCE_SERVICES)
    ]["Service"].dropna().unique()

    return invalid_services.tolist()


def validate_resource_inventory_duplicates(df):
    """
    Detect duplicate resources using Service + Resource_ID.
    """

    duplicate_mask = df.duplicated(
        subset=["Service", "Resource_ID"],
        keep=False
    )

    return int(duplicate_mask.sum())


def validate_resource_inventory_metadata(df):
    """
    Detect missing or Unknown FinOps metadata.
    """

    metadata_columns = [
        "Region",
        "Business_Unit",
        "Environment",
        "Owner"
    ]

    issues = {}

    for column in metadata_columns:
        missing_count = (
            df[column].isna() |
            df[column].astype(str).str.strip().eq("") |
            df[column].astype(str).str.strip().eq("Unknown")
        ).sum()

        if missing_count > 0:
            issues[column] = int(missing_count)

    return issues


def create_resource_inventory_quality_summary(
    invalid_services,
    duplicate_count,
    metadata_issues
):
    """
    Create a quality summary for the unified resource inventory.
    """

    summary = {}

    summary["invalid_services"] = (
        "PASS" if not invalid_services else "FAIL"
    )

    summary["duplicate_resources"] = (
        "PASS" if duplicate_count == 0 else "WARNING"
    )

    summary["missing_metadata"] = (
        "PASS" if not metadata_issues else "WARNING"
    )

    if "FAIL" in summary.values():
        summary["overall_status"] = "FAIL"
    elif "WARNING" in summary.values():
        summary["overall_status"] = "WARNING"
    else:
        summary["overall_status"] = "PASS"

    return summary


def validate_resource_inventory(df):
    """
    Run the complete resource inventory quality validation.
    """

    validate_resource_inventory_schema(df)

    invalid_services = (
        validate_resource_inventory_services(df)
    )

    duplicate_count = (
        validate_resource_inventory_duplicates(df)
    )

    metadata_issues = (
        validate_resource_inventory_metadata(df)
    )

    summary = create_resource_inventory_quality_summary(
        invalid_services=invalid_services,
        duplicate_count=duplicate_count,
        metadata_issues=metadata_issues
    )

    return {
        "invalid_services": invalid_services,
        "duplicate_count": duplicate_count,
        "metadata_issues": metadata_issues,
        "summary": summary
    }

