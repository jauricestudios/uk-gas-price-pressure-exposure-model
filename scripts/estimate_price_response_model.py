import pandas as pd
import statsmodels.api as sm
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)


input_path = PROCESSED_DATA / "gas_market_model_ready.csv"
df = pd.read_csv(input_path)

model_data = df.dropna(subset=[
    "nbp_return",
    "ttf_return",
    "nbp_lag_return",
    "gti"
]).copy()

X = model_data[["gti", "ttf_return", "nbp_lag_return"]]
X = sm.add_constant(X)

y = model_data["nbp_return"]

model = sm.OLS(y, X).fit()

print(model.summary())

coef_table = pd.DataFrame({
    "variable": model.params.index,
    "coefficient": model.params.values,
    "p_value": model.pvalues.values,
})

output_path = OUTPUT_TABLES / "price_response_coefficients.csv"
coef_table.to_csv(output_path, index=False)

print()
print(f"Saved coefficient table to: {output_path}")


