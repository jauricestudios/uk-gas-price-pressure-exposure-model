import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

gti_path = PROCESSED_DATA / "real_driver_gti_2026.csv"
gas_path = PROCESSED_DATA / "weekly_sap_gas_2026.csv"

gti = pd.read_csv(gti_path)
gas = pd.read_csv(gas_path)

gti["date"] = pd.to_datetime(gti["date"])
gas["date"] = pd.to_datetime(gas["date"])

# Keep the useful gas price columns.
gas = gas[[
    "date",
    "sap_price_gbp_per_mwh",
    "sap_7d_avg_gbp_per_mwh",
    "sap_weekly_return_pct"
]].copy()

gas["sap_price_change_gbp_per_mwh"] = gas["sap_price_gbp_per_mwh"].diff()

combined = pd.merge(
    gti,
    gas,
    on="date",
    how="inner"
)

output_path = PROCESSED_DATA / "gti_with_sap_gas_2026.csv"
combined.to_csv(output_path, index=False)

print("Joined Real-Driver GTI with real GB SAP gas prices.")
print(f"Saved file to: {output_path}")
print()
print(combined[[
    "date",
    "real_driver_gti",
    "sap_price_gbp_per_mwh",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct"
]].head(15))

print()
print("Correlation checks:")
print(
    "GTI vs SAP price level:",
    round(combined["real_driver_gti"].corr(combined["sap_price_gbp_per_mwh"]), 3)
)
print(
    "GTI vs weekly SAP price change:",
    round(combined["real_driver_gti"].corr(combined["sap_price_change_gbp_per_mwh"]), 3)
)
print(
    "GTI vs weekly SAP return %:",
    round(combined["real_driver_gti"].corr(combined["sap_weekly_return_pct"]), 3)
)

# Chart 1: GTI and gas price level over time
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(
    combined["date"],
    combined["real_driver_gti"],
    marker="o",
    label="Real-driver GTI"
)
ax1.axhline(0, linestyle="--")
ax1.set_xlabel("Date")
ax1.set_ylabel("GTI")

ax2 = ax1.twinx()
ax2.plot(
    combined["date"],
    combined["sap_price_gbp_per_mwh"],
    marker="s",
    label="SAP gas price"
)
ax2.set_ylabel("SAP gas price (£/MWh)")

plt.title("Real-Driver GTI and GB SAP Gas Price - 2026")
fig.autofmt_xdate()
fig.tight_layout()

chart_path = OUTPUT_CHARTS / "gti_vs_sap_gas_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")

# Chart 2: scatter plot of GTI vs weekly gas price change
plt.figure(figsize=(7, 5))
plt.scatter(
    combined["real_driver_gti"],
    combined["sap_price_change_gbp_per_mwh"]
)
plt.axhline(0, linestyle="--")
plt.axvline(0, linestyle="--")
plt.title("GTI vs Weekly SAP Gas Price Change")
plt.xlabel("Real-driver GTI")
plt.ylabel("Weekly SAP price change (£/MWh)")
plt.tight_layout()

scatter_path = OUTPUT_CHARTS / "gti_vs_sap_change_scatter_2026.png"
plt.savefig(scatter_path, dpi=150)

print(f"Saved scatter chart to: {scatter_path}")
