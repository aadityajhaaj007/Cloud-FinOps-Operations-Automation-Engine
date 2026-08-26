from src.config import load_config

from src.data_loader import load_cost_data

from src.data_validator import (
    validate_required_columns,
    validate_missing_values,
    validate_duplicates,
    validate_numeric_values,
    validate_dates,
    validate_categorical_values,
    create_validation_summary
)

from src.reconciliation import (
    load_control_total,
    reconcile_costs
)

from src.finops_metrics import generate_kpi_summary

from src.report_generator import generate_json_report
from src.excel_report import generate_excel_report
from src.pipeline_controller import should_continue
from src.logger import setup_logger
from src.anomaly_detector import (
    detect_anomalies,
    generate_anomaly_summary
)
from src.cost_intelligence import (
    calculate_savings_intelligence
)
from src.action_register import (
    generate_action_register
)
from src.action_governance import (
    apply_action_governance
)
from src.governance_intelligence import (
    calculate_governance_intelligence
)

from src.execution import (
    create_run_id,
    start_timer,
    calculate_duration
)


DATA_FILE = "data/input/aws_cost.csv"
CONTROL_FILE = "data/reference/billing_control.csv"


def main():

    # ----------------------------------------
    # 1. Start execution tracking
    # ----------------------------------------

    run_id = create_run_id()
    start_time = start_timer()

    logger = setup_logger()

    logger.info(
        f"FinOps pipeline started | Run ID: {run_id}"
    )


    # ----------------------------------------
    # 2. Load configuration
    # ----------------------------------------

    config = load_config()

    tolerance = config["reconciliation"]["tolerance"]

    cpu_threshold = config["optimization"]["cpu_threshold"]

    savings_assumption = config["optimization"]["savings_assumption"]

    # ----------------------------------------
    # 3. Load data
    # ----------------------------------------

    df = load_cost_data(DATA_FILE)

    logger.info(
        f"Loaded cost data successfully: {len(df)} records"
    )

    print("Data loaded successfully.")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")


    # ----------------------------------------
    # 4. Required columns validation
    # ----------------------------------------

    required_columns_ok = validate_required_columns(df)

    print("Required column validation: PASS")


    # ----------------------------------------
    # 5. Missing values validation
    # ----------------------------------------

    missing_values = validate_missing_values(df)

    if missing_values:
        print("Missing values detected:")
        print(missing_values)
    else:
        print("Missing value validation: PASS")


    # ----------------------------------------
    # 6. Duplicate validation
    # ----------------------------------------

    duplicate_count = validate_duplicates(df)

    if duplicate_count > 0:
        print(
            f"Duplicate records detected: "
            f"{duplicate_count}"
        )
    else:
        print("Duplicate record validation: PASS")


    # ----------------------------------------
    # 7. Numeric validation
    # ----------------------------------------

    numeric_issues = validate_numeric_values(df)

    if numeric_issues:
        print("Numeric validation issues detected:")
        print(numeric_issues)
    else:
        print("Numeric validation: PASS")


    # ----------------------------------------
    # 8. Date validation
    # ----------------------------------------

    invalid_date_count = validate_dates(df)

    if invalid_date_count > 0:
        print(
            f"Date validation issues detected: "
            f"{invalid_date_count}"
        )
    else:
        print("Date validation: PASS")


    # ----------------------------------------
    # 9. Categorical validation
    # ----------------------------------------

    categorical_issues = validate_categorical_values(df)

    if categorical_issues:
        print(
            "Categorical validation issues detected:"
        )
        print(categorical_issues)
    else:
        print("Categorical validation: PASS")


    # ----------------------------------------
    # 10. Validation summary
    # ----------------------------------------

    validation_summary = create_validation_summary(
        required_columns_ok,
        missing_values,
        duplicate_count,
        numeric_issues,
        invalid_date_count,
        categorical_issues
    )

    logger.info(
        f"Data quality status: "
        f"{validation_summary['overall_status']}"
    )

    print()
    print("=" * 50)
    print("DATA QUALITY SUMMARY")
    print("=" * 50)

    for check, status in validation_summary.items():
        print(f"{check:<25} {status}")

    print("=" * 50)


    # ----------------------------------------
    # 11. Cost reconciliation
    # ----------------------------------------

    expected_total = load_control_total(
        CONTROL_FILE
    )

    reconciliation_result = reconcile_costs(
        df,
        expected_total,
        tolerance
    )

    logger.info(
        f"Reconciliation status: "
        f"{reconciliation_result['status']} | "
        f"Difference: "
        f"₹{reconciliation_result['difference']:,.2f}"
    )

    print()
    print("=" * 50)
    print("COST RECONCILIATION")
    print("=" * 50)

    print(
        f"Expected total:  "
        f"₹{reconciliation_result['expected_total']:,.2f}"
    )

    print(
        f"Processed total: "
        f"₹{reconciliation_result['processed_total']:,.2f}"
    )

    print(
        f"Difference:      "
        f"₹{reconciliation_result['difference']:,.2f}"
    )

    print(
        f"Status:          "
        f"{reconciliation_result['status']}"
    )

    print(
        f"Tolerance:       "
        f"₹{reconciliation_result['tolerance']:,.2f}"
    )

    print("=" * 50)


    # ----------------------------------------
    # 12. Pipeline control
    # ----------------------------------------

    pipeline_ok, pipeline_message = should_continue(
        validation_summary,
        reconciliation_result
    )

    logger.info(
        f"Pipeline control: "
        f"{'CONTINUE' if pipeline_ok else 'STOP'} | "
        f"{pipeline_message}"
    )

    print()
    print("=" * 50)
    print("PIPELINE CONTROL")
    print("=" * 50)

    print(
        f"Status:  "
        f"{'CONTINUE' if pipeline_ok else 'STOP'}"
    )

    print(
        f"Message: {pipeline_message}"
    )

    print("=" * 50)


    if not pipeline_ok:

        logger.error(
            f"Pipeline stopped | Run ID: {run_id} | "
            f"Reason: {pipeline_message}"
        )

        print("Pipeline stopped.")
        return


    # ----------------------------------------
    # 13. Generate FinOps KPI summary
    # ----------------------------------------

    kpi_summary = generate_kpi_summary(
    df,
    cpu_threshold,
    savings_assumption
)

    print()
    print("=" * 50)
    print("FINOPS KPI SUMMARY")
    print("=" * 50)

    for metric, value in kpi_summary.items():
        print(f"{metric:<30} {value}")

    print("=" * 50)

    # ----------------------------------------
# 13. Anomaly detection
# ----------------------------------------

    anomaly_config = config["anomaly_detection"]

    anomalies = detect_anomalies(
        df,
        high_cost_threshold=anomaly_config["high_cost_threshold"],
        low_cpu_threshold=anomaly_config["low_cpu_threshold"]
)
    anomaly_summary = generate_anomaly_summary(
    anomalies
)
        # ----------------------------------------
    # 14. Cost savings intelligence
    # ----------------------------------------

    savings_intelligence = calculate_savings_intelligence(
        df,
        cpu_threshold,
        savings_assumption
    )
    print()
    print("=" * 50)
    print("COST SAVINGS INTELLIGENCE")
    print("=" * 50)

    print(
        f"Total spend:             "
        f"₹{savings_intelligence['total_spend']:,.2f}"
    )

    print(
        f"Optimization exposure:   "
        f"₹{savings_intelligence['optimization_exposure']:,.2f}"
    )

    print(
        f"Rightsizing exposure:    "
        f"₹{savings_intelligence['rightsizing_exposure']:,.2f}"
    )

    print(
        f"Estimated savings:       "
        f"₹{savings_intelligence['estimated_savings']:,.2f}"
    )

    print(
        f"Savings opportunity:     "
        f"{savings_intelligence['savings_percentage']:.2f}%"
    )



    print(
    f"Rightsizing candidates:  "
    f"{savings_intelligence['rightsizing_count']}"
)

    print("=" * 50)


   # ----------------------------------------
   # 15. Savings action register
   # ----------------------------------------

    action_register = generate_action_register(
        df,
        savings_intelligence
)
    created_date = (
    f"{run_id[:4]}-"
    f"{run_id[4:6]}-"
    f"{run_id[6:8]}"
)


    action_register = apply_action_governance(
        action_register,
        created_date=created_date,
        target_days=7
)

    governance_intelligence = calculate_governance_intelligence(
        action_register
)

    print()
    print("=" * 50)
    print("SAVINGS ACTION REGISTER")
    print("=" * 50)

    print(
        f"Action items: {len(action_register)}"
)


    if not action_register.empty:

        print(
            action_register[
            [
                "Action_ID",
                "Resource_ID",
                "Priority",
                "Estimated_Savings",
                "Action_Status",
                "Target_Date",
                "Days_Open",
                "SLA_Status"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("=" * 50)


    print()
    print("=" * 50)
    print("ANOMALY DETECTION")
    print("=" * 50)


    print(
       f"Total anomalies: {len(anomalies)}"
)

    if len(anomalies) > 0:

        print(
           anomalies[
            [
                "Anomaly_Rank",
                "Resource_ID",
                "Service",
                "Anomaly_Type",
                "Severity",
                "Monthly_Cost"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("=" * 50)

    governance_intelligence = calculate_governance_intelligence(
        action_register

)

    print()
    print("=" * 50)
    print("GOVERNANCE INTELLIGENCE")
    print("=" * 50)

    print(
        f"Total actions:              "
        f"{governance_intelligence['total_actions']}"
)

    print(
        f"Open actions:               "
        f"{governance_intelligence['open_actions']}"
)

    print(
        f"Completed actions:          "
        f"{governance_intelligence['completed_actions']}"
)

    print(
        f"On-track actions:           "
        f"{governance_intelligence['on_track_actions']}"
)

    print(
        f"At-risk actions:            "
        f"{governance_intelligence['at_risk_actions']}"
)

    print(
        f"Overdue actions:            "
        f"{governance_intelligence['overdue_actions']}"
)

    print(
        f"Escalated actions:          "
        f"{governance_intelligence['escalated_actions']}"
)

    print(
        f"High-priority actions:      "
        f"{governance_intelligence['high_priority_actions']}"
)

    print(
        f"Medium-priority actions:    "
        f"{governance_intelligence['medium_priority_actions']}"
)

    print(
        f"Open savings exposure:      "
        f"₹{governance_intelligence['open_savings_exposure']:,.2f}"
)

    print(
        f"Overdue savings exposure:   "
        f"₹{governance_intelligence['overdue_savings_exposure']:,.2f}"
)

    print(
        f"SLA compliance:             "
        f"{governance_intelligence['sla_compliance_percentage']:.2f}%"
)

    print("=" * 50)



    # ----------------------------------------
    # 14. Calculate execution duration
    # ----------------------------------------

    duration = calculate_duration(start_time)


    # ----------------------------------------
    # 15. Create execution metadata
    # ----------------------------------------

    execution_metadata = {
        "run_id": run_id,
        "records_processed": len(df),
        "total_spend": float(
            kpi_summary["total_spend"]
        ),
        "validation_status": (
            validation_summary["overall_status"]
        ),
        "reconciliation_status": (
            reconciliation_result["status"]
        ),
        "pipeline_status": "SUCCESS",
        "duration_seconds": round(
            duration,
            2
        )
    }


    # ----------------------------------------
    # 16. Generate JSON report
    # ----------------------------------------

    report_path = generate_json_report(
    "output/finops_summary.json",
    kpi_summary,
    validation_summary,
    reconciliation_result,
    execution_metadata,
    anomaly_summary,
    savings_intelligence,
    action_register,
    governance_intelligence
)

    print()
    print(
        f"JSON report generated: {report_path}"
    )
    # ----------------------------------------
# 17. Generate Excel report
# ----------------------------------------

    excel_report_path = generate_excel_report(
        output_path="output/finops_report.xlsx",
        df=df,
        kpi_summary=kpi_summary,
        validation_summary=validation_summary,
        reconciliation_result=reconciliation_result,
        cpu_threshold=cpu_threshold,
        savings_assumption=savings_assumption,
        anomaly_summary=anomaly_summary,
        anomalies=anomalies,
        savings_intelligence=savings_intelligence,
        action_register=action_register,
        governance_intelligence=governance_intelligence
)

    print()
    print(
    f"Excel report generated: "
    f"{excel_report_path}"
)

    # ----------------------------------------
    # 18. Execution summary
    # ----------------------------------------

    print()
    print("=" * 50)
    print("EXECUTION SUMMARY")
    print("=" * 50)

    print(
        f"Run ID:              {run_id}"
    )

    print(
        f"Records processed:   {len(df)}"
    )

    print(
        f"Total spend:         "
        f"₹{kpi_summary['total_spend']:,.2f}"
    )

    print(
        f"Validation:          "
        f"{validation_summary['overall_status']}"
    )

    print(
        f"Reconciliation:      "
        f"{reconciliation_result['status']}"
    )

    print(
        "Pipeline:             SUCCESS"
    )

    print(
        f"Duration:            "
        f"{duration:.2f} seconds"
    )

    print("=" * 50)


    # ----------------------------------------
    # 19. Log successful completion
    # ----------------------------------------

    logger.info(
        f"Pipeline completed successfully | "
        f"Run ID: {run_id} | "
        f"Records: {len(df)} | "
        f"Duration: {duration:.2f}s"
    )


# ----------------------------------------
# Application entry point
# ----------------------------------------

if __name__ == "__main__":
    try:
        main()

    except Exception as error:

        print()
        print("=" * 50)
        print("PIPELINE STATUS")
        print("=" * 50)
        print("Status: FAILED")
        print(f"Reason: {error}")
        print("=" * 50)

        logger = setup_logger()

        logger.error(
            f"Pipeline failed: {error}",
            exc_info=True
        )
