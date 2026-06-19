"""
Build a hedge sensitivity table for the UK gas buyer.

This shows how monthly cost impact changes under different hedge ratios.
It uses the commercial scenario table already created by:

    build_commercial_exposure_scenarios.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

SCENARIO_PATH = PROJECT_DIR / "data" / "processed" / "commercial_exposure_scenarios.csv"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

scenarios = pd.read_csv(SCENARIO_PATH)

monthly_volume = scenarios["monthly_gas_volume_mwh"].iloc[0]
current_price = scenarios["current_nbp_price_gbp_per_mwh"].iloc[0]

hedge_ratios = [0.00, 0.25, 0.50, 0.60, 0.75, 1.00]

rows = []

for _, scenario in scenarios.iterrows():
    for hedge_ratio in hedge_ratios:
        unhedged_volume = monthly_volume * (1 - hedge_ratio)

        price_change = (
            scenario["scenario_nbp_price_gbp_per_mwh"]
            - current_price
        )

        cost_impact = unhedged_volume * price_change

        rows.append({
            "scenario": scenario["scenario"],
            "price_shock_pct": scenario["price_shock_pct"],
            "hedge_ratio": hedge_ratio,
            "hedge_cover_pct": hedge_ratio * 100,
            "unhedged_volume_mwh": unhedged_volume,
            "cost_impact_gbp": cost_impact,
        })

sensitivity = pd.DataFrame(rows)

output_path = OUTPUT_TABLES / "hedge_sensitivity_table.csv"
sensitivity.to_csv(output_path, index=False)

print("Hedge sensitivity table")
print()
print(sensitivity)
print()
print(f"Saved table to: {output_path}")

# Exclude base case from chart because it is always zero.
plot_data = sensitivity[sensitivity["scenario"] != "Base case"].copy()

pivot = plot_data.pivot(
    index="hedge_cover_pct",
    columns="scenario",
    values="cost_impact_gbp"
)

plt.figure(figsize=(10, 5))

for scenario in pivot.columns:
    plt.plot(
        pivot.index,
        pivot[scenario],
        marker="o",
        label=scenario,
    )

plt.axhline(0, linewidth=1)
plt.title("Monthly Gas Cost Impact by Hedge Cover")
plt.xlabel("Hedge cover (%)")
plt.ylabel("Monthly cost impact (£)")
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "hedge_sensitivity_cost_impact.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved chart to: {chart_path}")
