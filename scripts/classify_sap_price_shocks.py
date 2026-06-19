import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "gti_with_sap_gas_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

# Size of weekly gas price move
df["abs_price_change"] = df["sap_price_change_gbp_per_mwh"].abs()

# Keep largest shock weeks only
shock_weeks = df.sort_values("abs_price_change", ascending=False).head(10).copy()


def classify_explanation(row):
    price_change = row["sap_price_change_gbp_per_mwh"]
    gti = row["real_driver_gti"]

    if price_change > 0 and gti > 0.75:
        return "Partly explained by tight physical conditions"
    elif price_change < 0 and gti < -0.75:
        return "Partly consistent with looser physical conditions"
    elif price_change > 0 and gti <= 0:
        return "Not explained by current GTI"
    elif price_change < 0 and gti >= 0:
        return "Not explained by current GTI"
    else:
        return "Weakly explained by current GTI"


def missing_driver(row):
    price_change = row["sap_price_change_gbp_per_mwh"]
    gti = row["real_driver_gti"]

    if price_change > 0 and gti <= 0:
        return "Likely missing supply, storage, LNG, TTF or risk-premium driver"
    elif price_change > 0 and gti > 0:
        return "GTI contributes, but market supply variables still needed"
    elif price_change < 0 and gti >= 0:
        return "Likely missing bearish supply, storage or market-pricing driver"
    else:
        return "Consistent direction, but needs broader gas-market confirmation"


shock_weeks["model_diagnostic"] = shock_weeks.apply(classify_explanation, axis=1)
shock_weeks["likely_missing_driver"] = shock_weeks.apply(missing_driver, axis=1)

shock_weeks = shock_weeks[[
    "date",
    "real_driver_gti",
    "hdd",
    "hdd_dev",
    "wind_shortfall",
    "sap_price_gbp_per_mwh",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct",
    "model_diagnostic",
    "likely_missing_driver"
]]

output_path = OUTPUT_TABLES / "sap_price_shock_diagnostic_table_2026.csv"
shock_weeks.to_csv(output_path, index=False)

print("SAP price shock diagnostic table")
print()
print(shock_weeks)
print()
print(f"Saved file to: {output_path}")
