from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Iterable


def build_validation_summary(
    monthly: Iterable[dict[str, Any]],
    baseline: float | None = None,
    post_optimization: float | None = None,
) -> dict[str, Any]:
    rows = list(monthly)
    latest = float(rows[-1].get("cost", 0)) if rows else None
    result: dict[str, Any] = {
        "baseline_cost": round(float(baseline), 2) if baseline is not None else None,
        "post_optimization_cost": round(float(post_optimization), 2) if post_optimization is not None else None,
        "latest_analyzed_cost": round(latest, 2) if latest is not None else None,
        "validation_status": "insufficient-evidence",
        "notes": [],
    }
    if baseline is None or post_optimization is None:
        result["notes"].append("Provide independently validated baseline and post-optimization periods before claiming realized savings.")
        return result
    delta = float(baseline) - float(post_optimization)
    result["observed_delta"] = round(delta, 2)
    result["observed_change_pct"] = round((delta / float(baseline)) * 100, 2) if baseline else None
    result["validation_status"] = "observed-reduction" if delta > 0 else "no-observed-reduction"
    result["notes"].append("Observed reduction is descriptive; attribution to a specific change requires supporting evidence.")
    return result


def build_export_bundle(report: dict[str, Any], validation: dict[str, Any] | None = None) -> dict[str, Any]:
    bundle = dict(report)
    bundle["exported_at"] = datetime.now(timezone.utc).isoformat()
    bundle["validation"] = validation or {"validation_status": "not-provided"}
    return bundle


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, default=str)


def report_to_csv(report: dict[str, Any]) -> str:
    rows = report.get("monthly_costs", [])
    output = io.StringIO()
    if not rows:
        return ""
    fieldnames = sorted({key for row in rows if isinstance(row, dict) for key in row})
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows({key: row.get(key) for key in fieldnames} for row in rows)
    return output.getvalue()


def report_to_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# FinOps Cost Report",
        "",
        f"Generated: `{report.get('generated_at', 'unknown')}`",
        "",
        "## Executive Summary",
        "",
        f"- Total analyzed cost: **${float(summary.get('total_analyzed_cost', 0)):,.2f}**",
        f"- Billing periods: **{summary.get('billing_periods', 0)}**",
        f"- Services: **{summary.get('services', 0)}**",
        f"- Anomalies: **{summary.get('anomalies', 0)}**",
        f"- Recommendation candidates: **{summary.get('recommendation_candidates', 0)}**",
        "",
        "## Service Totals",
        "",
        "| Service | Cost | |",
        "|---|---:|",
    ]
    lines[-2] = "| Service | Cost |"
    lines[-1] = "|---|---:|"
    for service, cost in sorted(report.get("service_totals", {}).items(), key=lambda item: float(item[1]), reverse=True):
        lines.append(f"| {service} | ${float(cost):,.2f} |")
    lines.extend(["", "## Findings", ""])
    findings = report.get("anomalies", []) + report.get("recommendations", [])
    if findings:
        for item in findings:
            label = item.get("reason") or item.get("signal") or item.get("title") or "Review candidate"
            lines.append(f"- **{label}**")
    else:
        lines.append("No findings were supplied to the report.")
    lines.extend(["", "## Limitations", ""])
    for limitation in report.get("limitations", []):
        lines.append(f"- {limitation}")
    validation = report.get("validation")
    if validation:
        lines.extend(["", "## Validation", "", f"- Status: **{validation.get('validation_status', 'unknown')}**"])
        if validation.get("observed_delta") is not None:
            lines.append(f"- Observed delta: **${float(validation['observed_delta']):,.2f}**")
        for note in validation.get("notes", []):
            lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
