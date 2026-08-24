import pandas as pd


def load_control_total(file_path):
    control_df = pd.read_csv(file_path)

    if control_df.empty:
        raise ValueError("Billing control file is empty.")

    required_columns = [
        "Billing_Date",
        "Expected_Total"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in control_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing control columns: {missing_columns}"
        )

    expected_total = control_df["Expected_Total"].iloc[0]

    return float(expected_total)


def reconcile_costs(df, expected_total, tolerance):
    processed_total = float(
        df["Monthly_Cost"].sum()
    )

    expected_total = float(expected_total)
    tolerance = float(tolerance)

    difference = expected_total - processed_total

    status = (
        "PASS"
        if abs(difference) <= tolerance
        else "FAIL"
    )

    return {
        "expected_total": expected_total,
        "processed_total": processed_total,
        "difference": float(difference),
        "tolerance": tolerance,
        "status": status
    }