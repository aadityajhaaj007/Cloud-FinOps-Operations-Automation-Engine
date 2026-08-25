import unittest
import pandas as pd

from src.action_governance import (
    apply_action_governance
)

from src.data_validator import (
    validate_required_columns,
    validate_missing_values,
    validate_duplicates,
    validate_numeric_values,
    validate_dates,
    validate_categorical_values,
    create_validation_summary,
)

from src.reconciliation import reconcile_costs

from src.finops_metrics import (
    calculate_total_spend,
    calculate_cost_by_service,
    calculate_cost_by_business_unit,
    calculate_average_cpu,
    calculate_low_utilization_resources,
    calculate_optimization_summary,
    generate_kpi_summary,
)

from src.optimization_engine import (
    generate_recommendation,
    generate_optimization_candidates,
)

from src.anomaly_detector import (
    detect_anomalies,
    generate_anomaly_summary,
)

from src.cost_intelligence import (
    calculate_savings_intelligence,
)

from src.action_register import (
    generate_action_register,
)

class TestFinOpsPipeline(unittest.TestCase):

    def setUp(self):

        self.df = pd.DataFrame({

            "Date": [
                "2026-01-31",
                "2026-01-31",
                "2026-01-31",
                "2026-01-31",
            ],

            "Resource_ID": [
                "res-001",
                "res-002",
                "res-003",
                "res-004",
            ],

            "Service": [
                "EC2",
                "RDS",
                "S3",
                "EBS",
            ],

            "Region": [
                "ap-south-1",
                "ap-south-1",
                "ap-south-1",
                "ap-south-1",
            ],

            "Business_Unit": [
                "Engineering",
                "Finance",
                "Marketing",
                "Engineering",
            ],

            "Environment": [
                "Production",
                "Production",
                "Development",
                "Testing",
            ],

            "CPU_Utilization": [
                10,
                50,
                20,
                80,
            ],

            "Storage_GB": [
                100,
                200,
                300,
                400,
            ],

            "Monthly_Cost": [
                10000,
                20000,
                15000,
                5000,
            ],

            "Owner": [
                "Team-A",
                "Team-B",
                "Team-C",
                "Team-A",
            ],

            "Resource_Status": [
                "Running",
                "Running",
                "Stopped",
                "Running",
            ],
        })

    # ========================================
    # V1.3 ACTION GOVERNANCE
    # ========================================

    def test_action_governance_fields(self):

        action_register = pd.DataFrame([
            {
                "Action_ID": "FIN-0001",
                "Priority": "HIGH",
                "Estimated_Savings": 8873.10
            }
        ])

        governed = apply_action_governance(
            action_register,
            created_date="2026-08-25",
            target_days=7
        )

        self.assertIn(
            "Created_Date",
            governed.columns
        )

        self.assertIn(
            "Target_Date",
            governed.columns
        )

        self.assertIn(
            "Completed_Date",
            governed.columns
        )

        self.assertIn(
            "Days_Open",
            governed.columns
        )

        self.assertIn(
            "SLA_Status",
            governed.columns
        )

    def test_action_governance_target_date(self):

        action_register = pd.DataFrame([
            {
                "Action_ID": "FIN-0001",
                "Priority": "HIGH",
                "Estimated_Savings": 8873.10
            }
        ])

        governed = apply_action_governance(
            action_register,
            created_date="2026-08-25",
            target_days=7
        )

        self.assertEqual(
            governed.iloc[0]["Target_Date"],
            pd.Timestamp("2026-09-01")
        )

    def test_action_governance_status(self):

        action_register = pd.DataFrame([
            {
                "Action_ID": "FIN-0001",
                "Priority": "HIGH",
                "Estimated_Savings": 8873.10
            }
        ])

        governed = apply_action_governance(
            action_register,
            created_date="2026-08-25",
            target_days=7
        )

        self.assertEqual(
            governed.iloc[0]["SLA_Status"],
            "ON_TRACK"
        )

    def test_action_governance_empty_register(self):

        action_register = pd.DataFrame(
            columns=[
                "Action_ID",
                "Priority",
                "Estimated_Savings"
            ]
        )

        governed = apply_action_governance(
            action_register,
            created_date="2026-08-25",
            target_days=7
        )

        self.assertTrue(
            governed.empty
        )

        self.assertIn(
            "SLA_Status",
            governed.columns
        )

    # ========================================
    # DATA VALIDATION
    # ========================================

    def test_required_columns(self):

        result = validate_required_columns(self.df)

        self.assertTrue(result)

    def test_missing_values(self):

        result = validate_missing_values(self.df)

        self.assertFalse(result)

    def test_duplicates(self):

        result = validate_duplicates(self.df)

        self.assertEqual(result, 0)

    def test_numeric_validation(self):

        result = validate_numeric_values(self.df)

        self.assertEqual(result, {})

    def test_date_validation(self):

        result = validate_dates(self.df)

        self.assertEqual(result, 0)

    def test_categorical_validation(self):

        result = validate_categorical_values(self.df)

        self.assertEqual(result, {})

    def test_validation_summary(self):

        summary = create_validation_summary(
            True,
            {},
            0,
            {},
            0,
            {}
        )

        self.assertEqual(
            summary["overall_status"],
            "PASS"
        )

    # ========================================
    # RECONCILIATION
    # ========================================

    def test_reconciliation(self):

        result = reconcile_costs(
            self.df,
            50000,
            1.00
        )

        self.assertEqual(
            result["status"],
            "PASS"
        )

        self.assertEqual(
            result["difference"],
            0
        )

    # ========================================
    # FINOPS METRICS
    # ========================================

    def test_total_spend(self):

        result = calculate_total_spend(self.df)

        self.assertEqual(
            result,
            50000
        )

    def test_cost_by_service(self):

        result = calculate_cost_by_service(self.df)

        self.assertEqual(
            result["RDS"],
            20000
        )

        self.assertEqual(
            result["EC2"],
            10000
        )

    def test_cost_by_business_unit(self):

        result = calculate_cost_by_business_unit(self.df)

        self.assertEqual(
            result["Finance"],
            20000
        )

    def test_average_cpu(self):

        result = calculate_average_cpu(self.df)

        self.assertEqual(
            result,
            40
        )

    def test_low_utilization(self):

        result = calculate_low_utilization_resources(
            self.df,
            30
        )

        # Only res-001 qualifies:
        # Running + CPU < 30

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result.iloc[0]["Resource_ID"],
            "res-001"
        )

    def test_optimization_summary(self):

        result = calculate_optimization_summary(
            self.df,
            30,
            0.30
        )

        self.assertEqual(
            result["rightsizing_candidates"],
            1
        )

        self.assertEqual(
            result["rightsizing_cost_exposure"],
            10000
        )

        self.assertEqual(
            result["estimated_rightsizing_savings"],
            3000
        )

    def test_kpi_summary(self):

        result = generate_kpi_summary(
            self.df,
            30,
            0.30
        )

        self.assertEqual(
            result["total_spend"],
            50000
        )

        self.assertEqual(
            result["resource_count"],
            4
        )

        self.assertEqual(
            result["service_count"],
            4
        )

        self.assertEqual(
            result["business_unit_count"],
            3
        )

        self.assertEqual(
            result["running_resources"],
            3
        )

        self.assertEqual(
            result["stopped_resources"],
            1
        )

        self.assertEqual(
            result["rightsizing_candidates"],
            1
        )

        self.assertEqual(
            result["stopped_resource_investigations"],
            1
        )

    # ========================================
    # ANOMALY DETECTION
    # ========================================

    def test_anomaly_detection(self):

        anomalies = detect_anomalies(
            self.df,
            high_cost_threshold=9000,
            low_cpu_threshold=20
        )

        self.assertGreater(
            len(anomalies),
            0
        )

        self.assertIn(
            "Anomaly_Type",
            anomalies.columns
        )

        self.assertIn(
            "Severity",
            anomalies.columns
        )

        self.assertIn(
            "Anomaly_Rank",
            anomalies.columns
        )

    def test_anomaly_summary(self):

        anomalies = detect_anomalies(
            self.df,
            high_cost_threshold=9000,
            low_cpu_threshold=20
        )

        summary = generate_anomaly_summary(
            anomalies
        )

        self.assertEqual(
            summary["total_anomalies"],
            5
        )

        self.assertEqual(
            summary["critical_anomalies"],
            2
        )

        self.assertEqual(
            summary["high_anomalies"],
            3
        )

        self.assertEqual(
            summary["high_cost_anomalies"],
            3
        )

        self.assertEqual(
            summary["low_utilization_high_cost"],
            1
        )

        self.assertEqual(
            summary["stopped_high_cost"],
            1
        )

    def test_anomaly_severity(self):

        anomalies = detect_anomalies(
            self.df,
            high_cost_threshold=9000,
            low_cpu_threshold=20
        )

        self.assertTrue(
            set(anomalies["Severity"]).issubset(
                {
                    "CRITICAL",
                    "HIGH",
                    "MEDIUM",
                    "LOW"
                }
            )
        )

    def test_anomaly_ranking(self):

        anomalies = detect_anomalies(
            self.df,
            high_cost_threshold=9000,
            low_cpu_threshold=20
        )

        self.assertEqual(
            anomalies["Anomaly_Rank"].tolist(),
            list(range(1, len(anomalies) + 1))
        )

    # ========================================
    # OPTIMIZATION ENGINE
    # ========================================

    def test_high_priority_rightsizing(self):

        row = self.df.iloc[0].copy()

        # HIGH requires:
        # CPU < 20
        # Cost >= 20,000

        row["Monthly_Cost"] = 25000

        result = generate_recommendation(
            row,
            30
        )

        self.assertEqual(
            result[0],
            "Rightsizing"
        )

        self.assertEqual(
            result[3],
            "HIGH"
        )

    def test_stopped_resource(self):

        row = self.df.iloc[2]

        result = generate_recommendation(
            row,
            30
        )

        self.assertEqual(
            result[0],
            "Stopped Resource Investigation"
        )

    def test_optimization_candidates(self):

        result = generate_optimization_candidates(
            self.df,
            30,
            0.30
        )

        self.assertEqual(
            len(result),
            2
        )

        self.assertIn(
            "Optimization_Rank",
            result.columns
        )

        self.assertIn(
            "Opportunity_Type",
            result.columns
        )

        self.assertIn(
            "Recommendation",
            result.columns
        )

        self.assertIn(
            "Priority",
            result.columns
        )

        self.assertIn(
            "Estimated_Savings",
            result.columns
        )

    def test_service_specific_recommendation(self):

        row = self.df.iloc[0].copy()

        row["Service"] = "EC2"

        result = generate_recommendation(
            row,
            30
        )

        self.assertIn(
            "EC2",
            result[2]
        )

    # ========================================
    # V1.1 COST INTELLIGENCE
    # ========================================

    def test_savings_intelligence(self):

        result = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        self.assertEqual(
            result["total_spend"],
            50000.0
        )

        self.assertAlmostEqual(
            result["estimated_savings"],
            3000.0,
            places=2
        )

        self.assertAlmostEqual(
            result["savings_percentage"],
            6.0,
            places=2
        )

        self.assertEqual(
            result["rightsizing_count"],
            1
        )


    def test_service_savings(self):

        result = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        service_savings = result[
            "service_savings"
        ]

        self.assertEqual(
            len(service_savings),
            1
        )

        self.assertAlmostEqual(
            service_savings.loc[
                "EC2",
                "estimated_savings"
            ],
            3000.0,
            places=2
        )


    def test_business_unit_savings(self):

        result = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        business_savings = result[
            "business_unit_savings"
        ]

        self.assertEqual(
            len(business_savings),
            1
        )

        self.assertAlmostEqual(
            business_savings.loc[
                "Engineering",
                "estimated_savings"
            ],
            3000.0,
            places=2
        )


    def test_top_savings_opportunities(self):

        result = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        top = result[
            "top_opportunities"
        ]

        self.assertEqual(
            len(top),
            1
        )

        self.assertEqual(
            top.iloc[0]["Resource_ID"],
            "res-001"
        )

        self.assertEqual(
            top.iloc[0]["Savings_Rank"],
            1
        )

        self.assertAlmostEqual(
            top.iloc[0]["Estimated_Savings"],
            3000.0,
            places=2
        )

    # ========================================
    # V1.2 SAVINGS ACTION REGISTER
    # ========================================

    def test_action_register(self):

        savings = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        result = generate_action_register(
            self.df,
            savings
        )

        self.assertEqual(
            len(result),
            1
        )

        self.assertEqual(
            result.iloc[0]["Action_ID"],
            "FIN-0001"
        )

        self.assertEqual(
            result.iloc[0]["Resource_ID"],
            "res-001"
        )

        self.assertEqual(
            result.iloc[0]["Action_Status"],
            "OPEN"
        )


    def test_action_register_owner(self):

        savings = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        result = generate_action_register(
            self.df,
            savings
        )

        self.assertEqual(
            result.iloc[0]["Owner"],
            "Team-A"
        )


    def test_action_register_savings(self):

        savings = calculate_savings_intelligence(
            self.df,
            cpu_threshold=30,
            savings_assumption=0.30
        )

        result = generate_action_register(
            self.df,
            savings
        )

        self.assertAlmostEqual(
            result.iloc[0]["Estimated_Savings"],
            3000.0,
            places=2
        )

if __name__ == "__main__":
    unittest.main()
