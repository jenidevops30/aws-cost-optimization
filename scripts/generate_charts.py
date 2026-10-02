#!/usr/bin/env python3
"""
Generate publication-quality charts for AWS Cost Optimization & FinOps Portfolio.
Outputs saved to analysis/ and architecture/
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Output directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set high-DPI and modern styling
plt.rcParams["figure.dpi"] = 300
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"]

# Modern FinOps Color Palette
DARK_BG = "#0f172a"      # Slate 900
PANEL_BG = "#1e293b"     # Slate 800
GRID_COLOR = "#334155"   # Slate 700
TEXT_MAIN = "#f8fafc"    # Slate 50
TEXT_MUTED = "#94a3b8"   # Slate 400
ACCENT_GREEN = "#10b981" # Emerald 500
ACCENT_BLUE = "#38bdf8"  # Sky 400
ACCENT_PURPLE = "#a855f7"# Purple 500
ACCENT_ORANGE = "#f97316"# Orange 500
ACCENT_RED = "#ef4444"   # Red 500


def plot_monthly_trend():
    """Generates the 9-month cost reduction trajectory chart."""
    months = ["Dec 2025", "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026"]
    costs = [813.43, 762.62, 500.50, 481.71, 467.80, 372.32, 327.07, 327.73, 357.36]

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)

    # Plot line & fill area
    ax.plot(months, costs, marker="o", markersize=8, color=ACCENT_BLUE, linewidth=2.8, label="Monthly AWS Spend ($)", zorder=4)
    ax.fill_between(months, costs, color=ACCENT_BLUE, alpha=0.15, zorder=3)

    # Annotate points
    for i, (m, c) in enumerate(zip(months, costs)):
        offset_y = 15 if i not in [0, 6] else 20
        ax.annotate(
            f"${c:.2f}",
            (m, c),
            textcoords="offset points",
            xytext=(0, offset_y),
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color=TEXT_MAIN,
            bbox=dict(boxstyle="round,pad=0.3", fc="#0f172a", ec=GRID_COLOR, lw=0.8)
        )

    # Callout for peak to trough
    ax.annotate(
        "Peak Spend: $813.43\n(Initial Audit)",
        xy=("Dec 2025", 813.43),
        xytext=(0.4, 850),
        fontsize=9,
        color="#fbbf24",
        fontweight="bold",
        ha="left"
    )

    ax.annotate(
        "Optimized: $327.07 (-59.8%)\nGraviton & RDS Rightsized",
        xy=("Jun 2026", 327.07),
        xytext=(4.8, 240),
        arrowprops=dict(facecolor=ACCENT_GREEN, edgecolor=ACCENT_GREEN, shrink=0.08, width=1.5, headwidth=6),
        fontsize=9.5,
        color=ACCENT_GREEN,
        fontweight="bold",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.4", fc="#064e3b", ec=ACCENT_GREEN, lw=1)
    )

    ax.set_ylim(180, 920)
    ax.set_title("AWS Monthly Cloud Spend Trajectory (Dec 2025 – Aug 2026)", fontsize=14, fontweight="bold", color=TEXT_MAIN, pad=18)
    ax.set_ylabel("Monthly Spend (USD $)", fontsize=11, color=TEXT_MUTED, labelpad=10)
    ax.tick_params(colors=TEXT_MUTED, labelsize=9.5)
    ax.grid(color=GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.7)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "monthly_spend_trend.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Generated: {chart_path}")


def plot_category_comparison():
    """Generates the before vs after cost comparison by infrastructure category."""
    categories = ["EC2 Instances", "RDS Database", "Load Balancing (ELB)", "VPC Networking", "EC2 Other (EBS/IPs)"]
    dec_costs = [244.96, 205.05, 116.88, 46.42, 29.89]
    jun_costs = [115.56, 79.72, 46.15, 24.98, 9.30]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)

    rects1 = ax.bar(x - width/2, dec_costs, width, label="Baseline (Dec 2025)", color="#ef4444", alpha=0.85, edgecolor="#f87171", zorder=3)
    rects2 = ax.bar(x + width/2, jun_costs, width, label="Optimized (Jun 2026)", color=ACCENT_GREEN, alpha=0.85, edgecolor="#34d399", zorder=3)

    # Add labels and percentage reductions
    for i in range(len(categories)):
        dec = dec_costs[i]
        jun = jun_costs[i]
        pct = ((jun - dec) / dec) * 100
        
        # Label on top of Dec bar
        ax.text(x[i] - width/2, dec + 4, f"${dec:.2f}", ha="center", va="bottom", fontsize=8.5, color=TEXT_MAIN, fontweight="bold")
        # Label on top of Jun bar
        ax.text(x[i] + width/2, jun + 4, f"${jun:.2f}", ha="center", va="bottom", fontsize=8.5, color=TEXT_MAIN, fontweight="bold")
        # Savings badge in the middle
        ax.text(x[i], max(dec, jun) + 20, f"{pct:.1f}%", ha="center", va="bottom", fontsize=9, color=ACCENT_GREEN, fontweight="heavy",
                bbox=dict(boxstyle="round,pad=0.25", fc="#064e3b", ec=ACCENT_GREEN, lw=0.8))

    ax.set_ylabel("Monthly Spend (USD $)", fontsize=11, color=TEXT_MUTED, labelpad=10)
    ax.set_title("Cost Category Reduction: Baseline vs. Optimized Spend", fontsize=14, fontweight="bold", color=TEXT_MAIN, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9.5, fontweight="medium", color=TEXT_MAIN)
    ax.set_ylim(0, 300)
    ax.tick_params(colors=TEXT_MUTED)
    ax.grid(axis="y", color=GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.7)

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    ax.legend(facecolor=DARK_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_MAIN, fontsize=10, loc="upper right")

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "category_cost_comparison.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Generated: {chart_path}")


def plot_savings_breakdown():
    """Generates a donut chart displaying total monthly savings distribution ($486.36 total)."""
    categories = [
        "EC2 Graviton Migration\n(-$129.40 / 35.2%)",
        "RDS Right-Sizing\n(-$125.33 / 34.1%)",
        "ELB Consolidation\n(-$70.72 / 19.2%)",
        "VPC Data Transfer\n(-$21.44 / 5.8%)",
        "EBS & Idle Cleanup\n(-$20.60 / 5.6%)"
    ]
    savings = [129.40, 125.33, 70.72, 21.44, 20.60]
    colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_ORANGE, "#f43f5e"]

    fig, ax = plt.subplots(figsize=(8.5, 6), facecolor=DARK_BG)
    ax.set_facecolor(PANEL_BG)

    wedges, texts, autotexts = ax.pie(
        savings,
        labels=categories,
        autopct="%1.1f%%",
        pctdistance=0.78,
        startangle=140,
        colors=colors,
        textprops=dict(color=TEXT_MAIN, fontsize=9.5),
        wedgeprops=dict(width=0.45, edgecolor=DARK_BG, linewidth=2)
    )

    for at in autotexts:
        at.set_color("#ffffff")
        at.set_fontweight("bold")
        at.set_fontsize(8.5)

    # Center circle annotation
    ax.text(0, 0.08, "Monthly Savings\nAchieved", ha="center", va="center", color=TEXT_MUTED, fontsize=10)
    ax.text(0, -0.15, "$486.36/mo\n(~60% cut)", ha="center", va="center", color=ACCENT_GREEN, fontsize=13, fontweight="bold")

    ax.set_title("Attribution of Monthly Cost Savings by FinOps Action", fontsize=13.5, fontweight="bold", color=TEXT_MAIN, pad=15)

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "savings_distribution.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Generated: {chart_path}")


if __name__ == "__main__":
    print("Generating FinOps portfolio charts...")
    plot_monthly_trend()
    plot_category_comparison()
    plot_savings_breakdown()
    print("All charts successfully generated!")
