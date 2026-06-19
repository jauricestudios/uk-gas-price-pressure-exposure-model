import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "gti_with_sap_gas_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

df["gti_lag_1"] = df["real_driver_gti"].shift(1)
df["gti_lag_2"] = df["real_driver_gti"].shift(2)
df["gti_lead_1"] = df["real_driver_gti"].shift(-1)

checks = {
    "same_week_gti_vs_price_change": df["real_driver_gti"].corr(df["sap_price_change_gbp_per_mwh"]),
    "lag_1_gti_vs_price_change": df["gti_lag_1"].corr(df["sap_price_change_gbp_per_mwh"]),
    "lag_2_gti_vs_price_change": df["gti_lag_2"].corr(df["sap_price_change_gbp_per_mwh"]),
    "lead_1_gti_vs_price_change": df["gti_lead_1"].corr(df["sap_price_change_gbp_per_mwh"]),
    "same_week_gti_vs_return_pct": df["real_driver_gti"].corr(df["sap_weekly_return_pct"]),
    "lag_1_gti_vs_return_pct": df["gti_lag_1"].corr(df["sap_weekly_return_pct"]),
    "lag_2_gti_vs_return_pct": df["gti_lag_2"].corr(df["sap_weekly_return_pct"]),
    "lead_1_gti_vs_return_pct": df["gti_lead_1"].corr(df["sap_weekly_return_pct"]),
}

results = pd.DataFrame(
    list(checks.items()),
    columns=["relationship", "correlation"]
)

output_path = OUTPUT_TABLES / "gti_lag_correlation_checks.csv"
results.to_csv(output_path, index=False)

print("GTI lag correlation checks")
print()
print(results)
print()
print(f"Saved file to: {output_path}")
