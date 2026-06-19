import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)


def z_score(series):
    mean = series.mean()
    std = series.std()

    if std == 0:
        return series * 0

    return (series - mean) / std


input_path = PROCESSED_DATA / "real_driver_inputs_2026.csv"
df = pd.read_csv(input_path)

df["date"] = pd.to_datetime(df["date"])

# Remove the first row because it is a partial week.
df = df.iloc[1:].copy()

# Standardise the real drivers.
df["hdd_z"] = z_score(df["hdd_dev"])
df["wind_shortfall_z"] = z_score(df["wind_shortfall"])

# First real-driver GTI.
# This version only uses real HDD and real wind data.
# Storage and LNG are not included yet.
df["real_driver_gti"] = (
    df["hdd_z"]
    + df["wind_shortfall_z"]
)

output_path = PROCESSED_DATA / "real_driver_gti_2026.csv"
df.to_csv(output_path, index=False)

print("Built real-driver Gas Tightness Index.")
print(f"Saved file to: {output_path}")
print()
print(df[[
    "date",
    "hdd",
    "hdd_dev",
    "wind_shortfall",
    "hdd_z",
    "wind_shortfall_z",
    "real_driver_gti"
]].head(10))

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["real_driver_gti"], marker="o")
plt.axhline(0, linestyle="--")
plt.title("Real-Driver Gas Tightness Index - 2026")
plt.xlabel("Date")
plt.ylabel("GTI")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "real_driver_gti_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
