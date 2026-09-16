from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_finops_report(
    monthly: list[dict[str, Any]],
    service_totals: dict[str, float],
    anomalies: list[dict[str, Any]] | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    correlation: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a machine-readable FinOps report without inventing evidence."""
    anomalies = anomalies or []
    recommendations = recommendations or []
    correlation = correlation or []
    total = sum(float(row.get("cost", 0)) for row in monthly)

    return {
        "report_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "cost_scope": "billing records supplied to the analysis",
            "resource_scope": "read-only inventory supplied to the analysis",
            "mode": "analysis-only",
        },
        "summary": {
            "total_analyzed_cost": round(total, 2),
            "billing_periods": len(monthly),
            "services": len(service_totals),
            "anomalies": len(anomalies),
            "recommendation_candidates": len(recommendations),
        },
        "monthly_costs": monthly,
        "service_totals": {k: round(float(v), 2) for k, v in service_totals.items()},
        "correlation": correlation,
        "anomalies": anomalies,
        "recommendations": recommendations,
        "limitations": [
            "Service-level billing is not treated as per-resource cost.",
            "Recommendations are candidates for review, not automatic changes.",
            "No AWS resource mutation is performed by report generation.",
        ],
    }
