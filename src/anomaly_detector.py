import pandas as pd


def detect_anomalies(
    df,
    high_cost_threshold=25000,
    low_cpu_threshold=20
):
    """
    Detect FinOps cost and utilization anomalies.

    Anomaly types:

    1. High Cost
    2. Low Utilization + High Cost
    3. Stopped Resource + High Cost
    """

    anomalies = []

    # ========================================
    # 1. High Cost
    # ========================================

    high_cost = df[
        df["Monthly_Cost"] >= high_cost_threshold
    ]

    for _, row in high_cost.iterrows():

        anomalies.append({
            "Resource_ID": row["Resource_ID"],
            "Service": row["Service"],
            "Business_Unit": row["Business_Unit"],
            "Environment": row["Environment"],
            "Resource_Status": row["Resource_Status"],
            "CPU_Utilization": row["CPU_Utilization"],
            "Monthly_Cost": row["Monthly_Cost"],
            "Anomaly_Type": "High Cost",
            "Severity": "HIGH",
            "Observed_Value": row["Monthly_Cost"],
            "Threshold": high_cost_threshold,
            "Recommendation": (
                "Review high monthly cost and "
                "validate resource sizing and usage"
            )
        })

    # ========================================
    # 2. Low Utilization + High Cost
    # ========================================

    low_utilization = df[
        (df["Resource_Status"] == "Running")
        &
        (df["CPU_Utilization"] < low_cpu_threshold)
        &
        (df["Monthly_Cost"] >= high_cost_threshold)
    ]

    for _, row in low_utilization.iterrows():

        anomalies.append({
            "Resource_ID": row["Resource_ID"],
            "Service": row["Service"],
            "Business_Unit": row["Business_Unit"],
            "Environment": row["Environment"],
            "Resource_Status": row["Resource_Status"],
            "CPU_Utilization": row["CPU_Utilization"],
            "Monthly_Cost": row["Monthly_Cost"],
            "Anomaly_Type": "Low Utilization + High Cost",
            "Severity": "CRITICAL",
            "Observed_Value": row["CPU_Utilization"],
            "Threshold": low_cpu_threshold,
            "Recommendation": (
                "Prioritize rightsizing investigation "
                "for this underutilized high-cost resource"
            )
        })

    # ========================================
    # 3. Stopped Resource + High Cost
    # ========================================

    stopped_high_cost = df[
        (df["Resource_Status"] == "Stopped")
        &
        (df["Monthly_Cost"] >= high_cost_threshold)
    ]

    for _, row in stopped_high_cost.iterrows():

        anomalies.append({
            "Resource_ID": row["Resource_ID"],
            "Service": row["Service"],
            "Business_Unit": row["Business_Unit"],
            "Environment": row["Environment"],
            "Resource_Status": row["Resource_Status"],
            "CPU_Utilization": row["CPU_Utilization"],
            "Monthly_Cost": row["Monthly_Cost"],
            "Anomaly_Type": "Stopped Resource + High Cost",
            "Severity": "CRITICAL",
            "Observed_Value": row["Monthly_Cost"],
            "Threshold": high_cost_threshold,
            "Recommendation": (
                "Investigate whether the stopped resource "
                "can be released, retired, or otherwise optimized"
            )
        })

    # ========================================
    # 4. Empty result handling
    # ========================================

    if not anomalies:

        return pd.DataFrame(
            columns=[
                "Resource_ID",
                "Service",
                "Business_Unit",
                "Environment",
                "Resource_Status",
                "CPU_Utilization",
                "Monthly_Cost",
                "Anomaly_Type",
                "Severity",
                "Observed_Value",
                "Threshold",
                "Recommendation",
                "Anomaly_Rank"
            ]
        )

    result = pd.DataFrame(anomalies)

    # ========================================
    # 5. Severity ranking
    # ========================================

    severity_order = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }

    result["Severity_Rank"] = (
        result["Severity"].map(severity_order)
    )

    # ========================================
    # 6. Sort anomalies
    # ========================================

    result = result.sort_values(
        by=[
            "Severity_Rank",
            "Monthly_Cost"
        ],
        ascending=[
            True,
            False
        ]
    ).reset_index(drop=True)

    # ========================================
    # 7. Anomaly rank
    # ========================================

    result["Anomaly_Rank"] = range(
        1,
        len(result) + 1
    )

    # ========================================
    # 8. Remove internal ranking column
    # ========================================

    result = result.drop(
        columns=["Severity_Rank"]
    )

    return result


def generate_anomaly_summary(anomalies):
    """
    Generate a compact summary of detected anomalies.
    """

    if anomalies.empty:

        return {
            "total_anomalies": 0,
            "critical_anomalies": 0,
            "high_anomalies": 0,
            "high_cost_anomalies": 0,
            "low_utilization_high_cost": 0,
            "stopped_high_cost": 0
        }

    return {
        "total_anomalies": int(
            len(anomalies)
        ),

        "critical_anomalies": int(
            (
                anomalies["Severity"]
                == "CRITICAL"
            ).sum()
        ),

        "high_anomalies": int(
            (
                anomalies["Severity"]
                == "HIGH"
            ).sum()
        ),

        "high_cost_anomalies": int(
            (
                anomalies["Anomaly_Type"]
                == "High Cost"
            ).sum()
        ),

        "low_utilization_high_cost": int(
            (
                anomalies["Anomaly_Type"]
                == "Low Utilization + High Cost"
            ).sum()
        ),

        "stopped_high_cost": int(
            (
                anomalies["Anomaly_Type"]
                == "Stopped Resource + High Cost"
            ).sum()
        )
    }