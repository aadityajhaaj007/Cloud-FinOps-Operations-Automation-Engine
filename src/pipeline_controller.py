def should_continue(
    validation_summary,
    reconciliation_result
):
    validation_status = validation_summary["overall_status"]
    reconciliation_status = reconciliation_result["status"]

    if validation_status == "FAIL":
        return False, "Data validation failed."

    if reconciliation_status == "FAIL":
        return False, "Cost reconciliation failed."

    return True, "Pipeline checks passed."