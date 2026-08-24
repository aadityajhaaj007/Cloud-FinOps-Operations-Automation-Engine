import json
from pathlib import Path


def generate_json_report(
    output_path,
    kpi_summary,
    validation_summary,
    reconciliation_result,
    execution_metadata,
    anomaly_summary=None
):

    if anomaly_summary is None:

        anomaly_summary = {
            "total_anomalies": 0,
            "critical_anomalies": 0,
            "high_anomalies": 0,
            "high_cost_anomalies": 0,
            "low_utilization_high_cost": 0,
            "stopped_high_cost": 0
        }

    report = {
        "execution": execution_metadata,

        "kpis": kpi_summary,

        "data_quality": validation_summary,

        "reconciliation": reconciliation_result,

        "anomalies": anomaly_summary
    }

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_file, "w") as file:

        json.dump(
            report,
            file,
            indent=4
        )

    return output_file