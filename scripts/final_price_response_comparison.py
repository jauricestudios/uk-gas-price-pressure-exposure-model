import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "sap_gti_nbp_ttf_market_context_2026.csv"
df = pd.read_csv(input_path)

model_data = df[[
    "sap_weekly_return_pct",
    "gti_v2_storage",
    "nbp_return_pct",
    "ttf_return_pct"
]].dropna().copy()

target = "sap_weekly_return_pct"

models = {
    "physical_gti_only": ["gti_v2_storage"],
    "market_context_only": ["nbp_return_pct", "ttf_return_pct"],
    "combined_physical_and_market": ["gti_v2_storage", "nbp_return_pct", "ttf_return_pct"]
}

rows = []

for model_name, features in models.items():
    X = model_data[features]
    y = model_data[target]

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict(X)
    r2 = r2_score(y, prediction)

    row = {
        "model": model_name,
        "features": ", ".join(features),
        "r_squared": r2,
        "intercept": model.intercept_
    }

    for feature, coef in zip(features, model.coef_):
        row[f"coef_{feature}"] = coef

    rows.append(row)

results = pd.DataFrame(rows)

output_path = OUTPUT_TABLES / "final_price_response_model_comparison.csv"
results.to_csv(output_path, index=False)

print("Final price response model comparison")
print()
print(results)
print()
print(f"Saved file to: {output_path}")
print()
print("Rows used:", len(model_data))
