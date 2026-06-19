import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

input_path = PROCESSED_DATA / "sap_gti_nbp_ttf_market_context_2026.csv"
df = pd.read_csv(input_path)
df["date"] = pd.to_datetime(df["date"])

model_data = df[[
    "date",
    "sap_weekly_return_pct",
    "nbp_return_pct",
    "ttf_return_pct"
]].dropna().copy()

X = model_data[["nbp_return_pct", "ttf_return_pct"]]
y = model_data["sap_weekly_return_pct"]

model = LinearRegression()
model.fit(X, y)

model_data["fitted_sap_return_pct"] = model.predict(X)

plt.figure(figsize=(10, 5))
plt.plot(
    model_data["date"],
    model_data["sap_weekly_return_pct"],
    marker="o",
    label="Actual SAP return"
)
plt.plot(
    model_data["date"],
    model_data["fitted_sap_return_pct"],
    marker="s",
    label="Fitted SAP return from NBP + TTF"
)
plt.axhline(0, linestyle="--")
plt.title("Actual vs Fitted SAP Weekly Returns - Market Context Model")
plt.xlabel("Date")
plt.ylabel("Weekly return (%)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "actual_vs_fitted_sap_market_model_2026.png"
plt.savefig(chart_path, dpi=150)

print("Saved chart to:", chart_path)
print()
print(model_data[[
    "date",
    "sap_weekly_return_pct",
    "fitted_sap_return_pct",
    "nbp_return_pct",
    "ttf_return_pct"
]])
