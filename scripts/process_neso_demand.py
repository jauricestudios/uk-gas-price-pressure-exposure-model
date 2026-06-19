import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)


input_path = RAW_DATA / "demanddata_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["SETTLEMENT_DATE"])

cols = [
    "date",
    "SETTLEMENT_PERIOD",
    "ND",
    "TSD",
    "ENGLAND_WALES_DEMAND",
    "EMBEDDED_WIND_GENERATION",
    "EMBEDDED_SOLAR_GENERATION",
]

df = df[cols].copy()

daily = (
    df.groupby("date")
      .agg({
          "ND": "mean",
          "TSD": "mean",
          "ENGLAND_WALES_DEMAND": "mean",
          "EMBEDDED_WIND_GENERATION": "mean",
          "EMBEDDED_SOLAR_GENERATION": "mean",
      })
      .reset_index()
)

weekly = (
    daily.set_index("date")
         .resample("W-FRI")
         .mean()
         .reset_index()
)

weekly["wind_shortfall"] = (
    weekly["EMBEDDED_WIND_GENERATION"].mean()
    - weekly["EMBEDDED_WIND_GENERATION"]
)

output_path = PROCESSED_DATA / "neso_weekly_wind_demand_2026.csv"
weekly.to_csv(output_path, index=False)

print("Processed NESO demand data.")
print(f"Saved file to: {output_path}")
print()
print(weekly.head(10))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly["date"],
    weekly["EMBEDDED_WIND_GENERATION"],
    marker="o"
)
plt.title("Weekly Embedded Wind Generation - NESO 2026")
plt.xlabel("Date")
plt.ylabel("Average embedded wind generation")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "neso_weekly_wind_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")

