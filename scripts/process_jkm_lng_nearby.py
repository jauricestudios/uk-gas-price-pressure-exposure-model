"""
Process Barchart Daily Nearby JKM LNG futures data.

JKM is usually quoted in USD/MMBtu.
For comparison with gas and power prices, it is converted into USD/MWh.

Unit conversion:
1 MWh = 3.412142 MMBtu

So:
JKM USD/MWh = JKM USD/MMBtu * 3.412142

Important:
This is a Barchart Daily Nearby rolling futures benchmark, not one fixed contract.
It is useful for global LNG price direction. To compare directly with UK NBP and
TTF in £/MWh, a GBP/USD exchange-rate series is also needed.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

jkm_path = RAW_DATA / "barchart_jkm_lng_daily_nearby_2021_2026.csv"

df = pd.read_csv(jkm_path)

df["date"] = pd.to_datetime(df["Time"], errors="coerce")
df = df.dropna(subset=["date"])

df["jkm_price_usd_per_mmbtu"] = pd.to_numeric(df["Latest"], errors="coerce")
df = df.dropna(subset=["jkm_price_usd_per_mmbtu"])

df = df[["date", "Symbol", "jkm_price_usd_per_mmbtu", "Volume", "Open Int"]]
df = df.rename(columns={"Symbol": "jkm_contract"})

df["jkm_price_usd_per_mwh"] = df["jkm_price_usd_per_mmbtu"] * 3.412142

df["jkm_log_return"] = np.log(
    df["jkm_price_usd_per_mwh"] / df["jkm_price_usd_per_mwh"].shift(1)
)

df["jkm_return_pct"] = df["jkm_log_return"] * 100

df = df.sort_values("date").reset_index(drop=True)

output_path = PROCESSED_DATA / "daily_barchart_jkm_lng_nearby_2021_2026.csv"
df.to_csv(output_path, index=False)

print("Processed JKM LNG Daily Nearby futures data")
print()
print(df.head())
print()
print(df.tail())
print()
print("Rows:", len(df))
print(f"Saved file to: {output_path}")

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["jkm_price_usd_per_mwh"])
plt.title("JKM LNG Nearby Futures, 2021-2026")
plt.xlabel("Date")
plt.ylabel("Price (USD/MWh)")
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "barchart_jkm_lng_nearby_usd_per_mwh_2021_2026.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved chart to: {chart_path}")
