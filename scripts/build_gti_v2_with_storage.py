import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

gti_path = PROCESSED_DATA / "gti_with_sap_gas_2026.csv"
storage_path = PROCESSED_DATA / "weekly_storage_stock_2026.csv"

gti = pd.read_csv(gti_path)
storage = pd.read_csv(storage_path)

gti["date"] = pd.to_datetime(gti["date"])
storage["date"] = pd.to_datetime(storage["date"])

storage = storage[[
    "date",
    "long_range_storage",
    "medium_range_storage",
    "short_range_storage",
    "total_storage_stock",
    "low_storage_pressure"
]].copy()

combined = pd.merge(
    gti,
    storage,
    on="date",
    how="inner"
)

combined["gti_v2_storage"] = (
    combined["hdd_z"]
    + combined["wind_shortfall_z"]
    + combined["low_storage_pressure"]
)

output_path = PROCESSED_DATA / "gti_v2_storage_with_sap_2026.csv"
combined.to_csv(output_path, index=False)

print("Built GTI v2 with storage.")
print(f"Saved file to: {output_path}")
print()
print(combined[[
    "date",
    "hdd_z",
    "wind_shortfall_z",
    "low_storage_pressure",
    "real_driver_gti",
    "gti_v2_storage",
    "sap_price_gbp_per_mwh",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct"
]].head(15))

print()
print("Correlation checks:")
print(
    "GTI v1 vs SAP price change:",
    round(combined["real_driver_gti"].corr(combined["sap_price_change_gbp_per_mwh"]), 3)
)
print(
    "GTI v2 storage vs SAP price change:",
    round(combined["gti_v2_storage"].corr(combined["sap_price_change_gbp_per_mwh"]), 3)
)
print(
    "GTI v1 vs SAP return %:",
    round(combined["real_driver_gti"].corr(combined["sap_weekly_return_pct"]), 3)
)
print(
    "GTI v2 storage vs SAP return %:",
    round(combined["gti_v2_storage"].corr(combined["sap_weekly_return_pct"]), 3)
)

# Save correlation comparison table
corr_table = pd.DataFrame({
    "relationship": [
        "GTI v1 vs SAP price change",
        "GTI v2 storage vs SAP price change",
        "GTI v1 vs SAP return %",
        "GTI v2 storage vs SAP return %"
    ],
    "correlation": [
        combined["real_driver_gti"].corr(combined["sap_price_change_gbp_per_mwh"]),
        combined["gti_v2_storage"].corr(combined["sap_price_change_gbp_per_mwh"]),
        combined["real_driver_gti"].corr(combined["sap_weekly_return_pct"]),
        combined["gti_v2_storage"].corr(combined["sap_weekly_return_pct"])
    ]
})

corr_path = OUTPUT_TABLES / "gti_v1_v2_storage_correlation_check.csv"
corr_table.to_csv(corr_path, index=False)

print()
print(f"Saved correlation table to: {corr_path}")

# Chart: GTI v1 vs GTI v2
plt.figure(figsize=(10, 5))
plt.plot(combined["date"], combined["real_driver_gti"], marker="o", label="GTI v1: HDD + wind")
plt.plot(combined["date"], combined["gti_v2_storage"], marker="s", label="GTI v2: HDD + wind + storage")
plt.axhline(0, linestyle="--")
plt.title("GTI v1 vs GTI v2 with Storage - 2026")
plt.xlabel("Date")
plt.ylabel("GTI")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "gti_v1_vs_v2_storage_2026.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved GTI comparison chart to: {chart_path}")

# Chart: GTI v2 and SAP price
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(combined["date"], combined["gti_v2_storage"], marker="o", label="GTI v2")
ax1.axhline(0, linestyle="--")
ax1.set_xlabel("Date")
ax1.set_ylabel("GTI v2")

ax2 = ax1.twinx()
ax2.plot(combined["date"], combined["sap_price_gbp_per_mwh"], marker="s", label="SAP gas price")
ax2.set_ylabel("SAP gas price (£/MWh)")

plt.title("GTI v2 with Storage and GB SAP Gas Price - 2026")
fig.autofmt_xdate()
fig.tight_layout()

chart_path_2 = OUTPUT_CHARTS / "gti_v2_storage_vs_sap_2026.png"
plt.savefig(chart_path_2, dpi=150)

print(f"Saved GTI v2 vs SAP chart to: {chart_path_2}")
