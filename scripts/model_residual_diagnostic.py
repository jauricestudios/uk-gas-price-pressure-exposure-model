import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "sap_gti_nbp_ttf_market_context_2026.csv"

df = pd.read_csv(input_path)
df["date"] = pd.to_datetime(df["date"])

# Recreate fitted values from the final market-context model:
# SAP return = intercept + coef_NBP * NBP return + coef_TTF * TTF return
intercept = 0.920573
coef_nbp = -0.511743
coef_ttf = 0.922300

model_data = df[[
    "date",
    "sap_weekly_return_pct",
    "nbp_return_pct",
    "ttf_return_pct",
    "gti_v2_storage"
]].dropna().copy()

model_data["fitted_sap_return_pct"] = (
    intercept
    + coef_nbp * model_data["nbp_return_pct"]
    + coef_ttf * model_data["ttf_return_pct"]
)

model_data["model_error_pct_points"] = (
    model_data["sap_weekly_return_pct"]
    - model_data["fitted_sap_return_pct"]
)

model_data["absolute_error_pct_points"] = (
    model_data["model_error_pct_points"].abs()
)

model_data["diagnostic_note"] = model_data["absolute_error_pct_points"].apply(
    lambda x: "large miss - needs local/lagged explanation" if x >= 8 else "reasonable fit"
)

output_path = OUTPUT_TABLES / "model_residual_diagnostic_2026.csv"
model_data.to_csv(output_path, index=False)

print("Model residual diagnostic")
print()
print(model_data.sort_values("absolute_error_pct_points", ascending=False))
print()
print(f"Saved file to: {output_path}")
