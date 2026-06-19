import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

gti_v2_path = PROCESSED_DATA / "gti_v2_storage_with_sap_2026.csv"
lng_path = PROCESSED_DATA / "weekly_lng_terminal_flows_2026.csv"

gti = pd.read_csv(gti_v2_path)
lng = pd.read_csv(lng_path)

gti["date"] = pd.to_datetime(gti["date"])
lng["date"] = pd.to_datetime(lng["date"])

lng = lng[[
    "date",
    "isle_of_grain_lng_outflow",
    "south_hook_lng_outflow",
    "dragon_lng_outflow",
    "total_lng_outflow",
    "low_lng_sendout_pressure"
]].copy()

combined = pd.merge(
    gti,
    lng,
    on="date",
    how="inner"
)

combined["gti_v3_lng"] = (
    combined["hdd_z"]
    + combined["wind_shortfall_z"]
    + combined["low_storage_pressure"]
    + combined["low_lng_sendout_pressure"]
)

output_path = PROCESSED_DATA / "gti_v3_lng_with_sap_2026.csv"
combined.to_csv(output_path, index=False)

print("Built GTI v3 with storage and LNG.")
print(f"Saved file to: {output_path}")
print()
print(combined[[
    "date",
    "hdd_z",
    "wind_shortfall_z",
    "low_storage_pressure",
    "low_lng_sendout_pressure",
    "real_driver_gti",
    "gti_v2_storage",
    "gti_v3_lng",
    "sap_price_gbp_per_mwh",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct"
]].head(20))

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
    "GTI v3 storage + LNG vs SAP price change:",
    round(combined["gti_v3_lng"].corr(combined["sap_price_change_gbp_per_mwh"]), 3)
)
print(
    "GTI v1 vs SAP return %:",
    round(combined["real_driver_gti"].corr(combined["sap_weekly_return_pct"]), 3)
)
print(
    "GTI v2 storage vs SAP return %:",
    round(combined["gti_v2_storage"].corr(combined["sap_weekly_return_pct"]), 3)
)
print(
    "GTI v3 storage + LNG vs SAP return %:",
    round(combined["gti_v3_lng"].corr(combined["sap_weekly_return_pct"]), 3)
)

corr_table = pd.DataFrame({
    "relationship": [
        "GTI v1 vs SAP price change",
        "GTI v2 storage vs SAP price change",
        "GTI v3 storage + LNG vs SAP price change",
        "GTI v1 vs SAP return %",
        "GTI v2 storage vs SAP return %",
        "GTI v3 storage + LNG vs SAP return %"
    ],
    "correlation": [
        combined["real_driver_gti"].corr(combined["sap_price_change_gbp_per_mwh"]),
        combined["gti_v2_storage"].corr(combined["sap_price_change_gbp_per_mwh"]),
        combined["gti_v3_lng"].corr(combined["sap_price_change_gbp_per_mwh"]),
        combined["real_driver_gti"].corr(combined["sap_weekly_return_pct"]),
        combined["gti_v2_storage"].corr(combined["sap_weekly_return_pct"]),
        combined["gti_v3_lng"].corr(combined["sap_weekly_return_pct"])
    ]
})

corr_path = OUTPUT_TABLES / "gti_v1_v2_v3_correlation_check.csv"
corr_table.to_csv(corr_path, index=False)

print()
print(f"Saved correlation table to: {corr_path}")

# Chart 1: compare GTI versions
plt.figure(figsize=(10, 5))
plt.plot(combined["date"], combined["real_driver_gti"], marker="o", label="GTI v1: HDD + wind")
plt.plot(combined["date"], combined["gti_v2_storage"], marker="s", label="GTI v2: + storage")
plt.plot(combined["date"], combined["gti_v3_lng"], marker="^", label="GTI v3: + storage + LNG")
plt.axhline(0, linestyle="--")
plt.title("GTI Versions Compared - 2026")
plt.xlabel("Date")
plt.ylabel("GTI")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "gti_versions_compared_2026.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved GTI versions chart to: {chart_path}")

# Chart 2: GTI v3 and SAP price
fig, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(combined["date"], combined["gti_v3_lng"], marker="o", label="GTI v3")
ax1.axhline(0, linestyle="--")
ax1.set_xlabel("Date")
ax1.set_ylabel("GTI v3")

ax2 = ax1.twinx()
ax2.plot(combined["date"], combined["sap_price_gbp_per_mwh"], marker="s", label="SAP gas price")
ax2.set_ylabel("SAP gas price (£/MWh)")

plt.title("GTI v3 with Storage/LNG and GB SAP Gas Price - 2026")
fig.autofmt_xdate()
fig.tight_layout()

chart_path_2 = OUTPUT_CHARTS / "gti_v3_lng_vs_sap_2026.png"
plt.savefig(chart_path_2, dpi=150)

print(f"Saved GTI v3 vs SAP chart to: {chart_path_2}")

# Diagnostic rows around the March shock
march_rows = combined[
    (combined["date"] >= "2026-02-27")
    & (combined["date"] <= "2026-03-20")
][[
    "date",
    "hdd_z",
    "wind_shortfall_z",
    "low_storage_pressure",
    "low_lng_sendout_pressure",
    "gti_v3_lng",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct"
]]

march_path = OUTPUT_TABLES / "march_price_shock_gti_v3_diagnostic.csv"
march_rows.to_csv(march_path, index=False)

print()
print("March shock diagnostic:")
print(march_rows)
print()
print(f"Saved March diagnostic table to: {march_path}")
