import pandas as pd

REQUIRED_COLUMNS = [
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


ALLOWED_VALUES = {
    "Service": [
        "CloudFront",
        "EBS",
        "EC2",
        "Lambda",
        "RDS",
        "S3"
    ],

    "Environment": [
        "Development",
        "Production",
        "Testing"
    ],

    "Resource_Status": [
        "Running",
        "Stopped"
    ]
}


def validate_required_columns(df):
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


def validate_missing_values(df):
    missing_values = df.isna().sum()

    columns_with_missing = missing_values[
        missing_values > 0
    ]

    if not columns_with_missing.empty:
        return columns_with_missing.to_dict()

    return {}

# Validate duplicate records 
def validate_duplicates(df):
    duplicate_count = df.duplicated().sum()

    return duplicate_count

#Validate numeric values 

def validate_numeric_values(df):
    issues = {}

    invalid_cpu = df[
        (df["CPU_Utilization"] < 0) |
        (df["CPU_Utilization"] > 100)
    ]

    if not invalid_cpu.empty:
        issues["invalid_cpu"] = len(invalid_cpu)

    invalid_storage = df[
        df["Storage_GB"] < 0
    ]

    if not invalid_storage.empty:
        issues["invalid_storage"] = len(invalid_storage)

    invalid_cost = df[
        df["Monthly_Cost"] < 0
    ]

    if not invalid_cost.empty:
        issues["invalid_cost"] = len(invalid_cost)

    # Validate numeric values
        numeric_issues = validate_numeric_values(df)
    
        if numeric_issues:
            print("Numeric validation issues detected:")
            print(numeric_issues)
        else:
            print("Numeric validation: PASS")


    return issues

def validate_dates(df):
    invalid_dates = pd.to_datetime(
        df["Date"],
        errors="coerce"
    ).isna()

    invalid_count = invalid_dates.sum()

    return invalid_count      

def validate_categorical_values(df):
    issues = {}

    for column, allowed_values in ALLOWED_VALUES.items():

        invalid_values = df[
            ~df[column].isin(allowed_values)
        ][column].unique()

        if len(invalid_values) > 0:
            issues[column] = invalid_values.tolist()

    return issues  

def create_validation_summary(
    required_columns_ok,
    missing_values,
    duplicate_count,
    numeric_issues,
    invalid_date_count,
    categorical_issues
):
    summary = {}

    summary["required_columns"] = (
        "PASS" if required_columns_ok else "FAIL"
    )

    summary["missing_values"] = (
        "PASS" if not missing_values else "WARNING"
    )

    summary["duplicates"] = (
        "PASS" if duplicate_count == 0 else "WARNING"
    )

    summary["numeric_values"] = (
        "PASS" if not numeric_issues else "FAIL"
    )

    summary["dates"] = (
        "PASS" if invalid_date_count == 0 else "FAIL"
    )

    summary["categorical_values"] = (
        "PASS" if not categorical_issues else "FAIL"
    )

    if "FAIL" in summary.values():
        summary["overall_status"] = "FAIL"
    elif "WARNING" in summary.values():
        summary["overall_status"] = "WARNING"
    else:
        summary["overall_status"] = "PASS"

    return summary