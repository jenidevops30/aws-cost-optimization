import unittest

from src.cost_engine import CostRecord, month_over_month, monthly_totals, service_totals


class CostEngineTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            CostRecord("2026-01", "EC2", "compute", "us-east-1", 120),
            CostRecord("2026-01", "RDS", "db", "us-east-1", 80),
            CostRecord("2026-02", "EC2", "compute", "us-east-1", 90),
            CostRecord("2026-02", "RDS", "db", "us-east-1", 70),
        ]

    def test_monthly_totals(self):
        self.assertEqual(monthly_totals(self.records), {"2026-01": 200, "2026-02": 160})

    def test_service_totals(self):
        self.assertEqual(service_totals(self.records)["EC2"], 210)
        self.assertEqual(service_totals(self.records)["RDS"], 150)

    def test_month_over_month(self):
        result = month_over_month(self.records)
        self.assertIsNone(result[0]["change"])
        self.assertEqual(result[1]["change"], -40)
        self.assertAlmostEqual(result[1]["change_pct"], -20.0)


if __name__ == "__main__":
    unittest.main()
