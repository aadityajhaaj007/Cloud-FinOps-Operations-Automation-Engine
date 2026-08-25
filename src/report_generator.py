import json
from pathlib import Path


def generate_json_report(
    output_path,
    kpi_summary,
    validation_summary,
    reconciliation_result,
    execution_metadata,
    anomaly_summary=None,
    savings_intelligence=None,
    action_register=None
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

    if savings_intelligence is None:

        savings_report = {
            "total_spend": 0.0,
            "optimization_exposure": 0.0,
            "rightsizing_exposure": 0.0,
            "estimated_savings": 0.0,
            "savings_percentage": 0.0,
            "rightsizing_count": 0,
            "service_savings": [],
            "business_unit_savings": [],
            "top_opportunities": []
        }

    else:

        service_savings = savings_intelligence.get(
            "service_savings"
        )

        business_unit_savings = savings_intelligence.get(
            "business_unit_savings"
        )

        top_opportunities = savings_intelligence.get(
            "top_opportunities"
        )

        if service_savings is not None:
            service_savings = (
                service_savings
                .reset_index()
                .to_dict(orient="records")
            )
        else:
            service_savings = []

        if business_unit_savings is not None:
            business_unit_savings = (
                business_unit_savings
                .reset_index()
                .to_dict(orient="records")
            )
        else:
            business_unit_savings = []

        if top_opportunities is not None:
            top_opportunities = (
                top_opportunities
                .to_dict(orient="records")
            )
        else:
            top_opportunities = []

        savings_report = {
            "total_spend": float(
                savings_intelligence["total_spend"]
            ),
            "optimization_exposure": float(
                savings_intelligence["optimization_exposure"]
            ),
            "rightsizing_exposure": float(
                savings_intelligence["rightsizing_exposure"]
            ),
            "estimated_savings": float(
                savings_intelligence["estimated_savings"]
            ),
            "savings_percentage": float(
                savings_intelligence["savings_percentage"]
            ),
            "rightsizing_count": int(
                savings_intelligence["rightsizing_count"]
            ),
            "service_savings": service_savings,
            "business_unit_savings": business_unit_savings,
            "top_opportunities": top_opportunities
        }

    if action_register is not None:

        if hasattr(action_register, "to_dict"):
            action_register_report = (
                action_register
                .to_dict(orient="records")
            )
        else:
            action_register_report = action_register

    else:
        action_register_report = []

    report = {
        "execution": execution_metadata,
        "kpis": kpi_summary,
        "data_quality": validation_summary,
        "reconciliation": reconciliation_result,
        "anomalies": anomaly_summary,
        "savings_intelligence": savings_report,
        "action_register": action_register_report
    }

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    return output_file
