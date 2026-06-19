import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)


input_path = PROCESSED_DATA / "weather_daily_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

# Heating Degree Days.
# A common base temperature is 15.5°C.
# If the average temperature is below 15.5°C, heating demand is assumed to rise.
base_temperature = 15.5
df["hdd"] = (base_temperature - df["avg_temperature_c"]).clip(lower=0)

# Convert daily HDD into weekly HDD.
# W-FRI means each week ends on Friday.
weekly_hdd = (
    df.set_index("date")
      .resample("W-FRI")
      .agg({
          "avg_temperature_c": "mean",
          "hdd": "sum"
      })
      .reset_index()
)

# With only 2026 data, the deviation is measured against the sample average.
# Later, with multi-year data, we will compare each week against its seasonal normal.
weekly_hdd["hdd_dev"] = weekly_hdd["hdd"] - weekly_hdd["hdd"].mean()

output_path = PROCESSED_DATA / "weather_weekly_hdd_2026.csv"
weekly_hdd.to_csv(output_path, index=False)

print("Built weekly HDD data.")
print(f"Saved file to: {output_path}")
print()
print(weekly_hdd.head(10))

plt.figure(figsize=(10, 5))
plt.plot(weekly_hdd["date"], weekly_hdd["hdd"], marker="o")
plt.title("Weekly Heating Degree Days - 2026")
plt.xlabel("Date")
plt.ylabel("Weekly HDD")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_hdd_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")


