import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("Starting Gas Tightness Index script...")

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)


def z_score(series):
    mean = series.mean()
    std = series.std()

    if std == 0:
        return series * 0

    return (series - mean) / std


def build_gti(df):
    df = df.copy()

    df["hdd_z"] = z_score(df["hdd_dev"])
    df["storage_z"] = z_score(df["storage_dev"])
    df["lng_z"] = z_score(df["lng_dev"])
    df["wind_z"] = z_score(df["wind_shortfall"])

    df["gti"] = (
        df["hdd_z"]
        - df["storage_z"]
        - df["lng_z"]
        + df["wind_z"]
    )

    return df


dates = pd.date_range(start="2025-01-03", periods=12, freq="W-FRI")

test_data = pd.DataFrame({
    "date": dates,
    "hdd_dev": [0.1, 0.3, 0.8, 1.1, 0.7, 0.2, -0.1, -0.4, -0.2, 0.1, 0.4, 0.6],
    "storage_dev": [0.2, 0.1, -0.2, -0.5, -0.4, -0.1, 0.1, 0.3, 0.4, 0.2, -0.1, -0.3],
    "lng_dev": [0.1, 0.0, -0.2, -0.4, -0.1, 0.2, 0.3, 0.1, 0.0, -0.1, -0.3, -0.4],
    "wind_shortfall": [0.0, 0.2, 0.5, 0.9, 0.7, 0.1, -0.2, -0.3, -0.1, 0.2, 0.5, 0.8],
})

gti_data = build_gti(test_data)

output_csv = OUTPUT_TABLES / "gti_test_output.csv"
gti_data.to_csv(output_csv, index=False)

print("\nGas Tightness Index test output:")
print(gti_data[["date", "hdd_dev", "storage_dev", "lng_dev", "wind_shortfall", "gti"]])

print(f"\nSaved table to: {output_csv}")

plt.figure(figsize=(10, 5))
plt.plot(gti_data["date"], gti_data["gti"], marker="o")
plt.axhline(0, linestyle="--")
plt.title("Gas Tightness Index - Test Data")
plt.xlabel("Date")
plt.ylabel("GTI")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "gti_test_chart.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved chart to: {chart_path}")
print("Script finished.")


