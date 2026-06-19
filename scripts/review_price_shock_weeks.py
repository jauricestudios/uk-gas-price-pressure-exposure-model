import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "gti_with_sap_gas_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

df["abs_price_change"] = df["sap_price_change_gbp_per_mwh"].abs()
df["abs_return_pct"] = df["sap_weekly_return_pct"].abs()

shock_weeks = (
    df
    .sort_values("abs_price_change", ascending=False)
    [[
        "date",
        "real_driver_gti",
        "hdd",
        "hdd_dev",
        "wind_shortfall",
        "sap_price_gbp_per_mwh",
        "sap_price_change_gbp_per_mwh",
        "sap_weekly_return_pct"
    ]]
    .head(10)
)

output_path = OUTPUT_TABLES / "largest_sap_price_shock_weeks_2026.csv"
shock_weeks.to_csv(output_path, index=False)

print("Largest weekly SAP gas price moves")
print()
print(shock_weeks)
print()
print(f"Saved file to: {output_path}")
