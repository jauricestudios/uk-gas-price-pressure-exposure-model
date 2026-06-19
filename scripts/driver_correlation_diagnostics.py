import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "gti_v3_lng_with_sap_2026.csv"
df = pd.read_csv(input_path)

drivers = [
    "hdd_z",
    "wind_shortfall_z",
    "low_storage_pressure",
    "low_lng_sendout_pressure",
    "real_driver_gti",
    "gti_v2_storage",
    "gti_v3_lng"
]

target_1 = "sap_price_change_gbp_per_mwh"
target_2 = "sap_weekly_return_pct"

rows = []

for driver in drivers:
    rows.append({
        "driver": driver,
        "corr_with_sap_price_change": df[driver].corr(df[target_1]),
        "corr_with_sap_return_pct": df[driver].corr(df[target_2])
    })

results = pd.DataFrame(rows)
results = results.sort_values("corr_with_sap_price_change", ascending=False)

output_path = OUTPUT_TABLES / "driver_correlation_diagnostics_2026.csv"
results.to_csv(output_path, index=False)

print("Driver correlation diagnostics")
print()
print(results)
print()
print(f"Saved file to: {output_path}")
