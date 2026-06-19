"""
Convert Dutch TTF nearby futures from EUR/MWh into GBP/MWh using EUR/GBP.

This allows UK NBP and Dutch TTF to be compared on a common currency basis.

Inputs:
- daily_barchart_nbp_ttf_nearby_2021_2026.csv
- barchart_eurgbp_daily_2021_2026.csv

Outputs:
- daily_barchart_nbp_ttf_nearby_with_fx_2021_2026.csv
- chart comparing NBP £/MWh and TTF £/MWh
- chart showing the NBP-TTF spread in £/MWh
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
RAW_DATA = PROJECT_DIR / "data" / "raw"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

gas_path = PROCESSED_DATA / "daily_barchart_nbp_ttf_nearby_2021_2026.csv"
fx_path = RAW_DATA / "barchart_eurgbp_daily_2021_2026.csv"

gas = pd.read_csv(gas_path, parse_dates=["date"])
fx = pd.read_csv(fx_path)

fx["date"] = pd.to_datetime(fx["Time"], errors="coerce")
fx = fx.dropna(subset=["date"])

fx["eur_gbp"] = pd.to_numeric(fx["Latest"], errors="coerce")
fx = fx.dropna(subset=["eur_gbp"])

fx = fx[["date", "eur_gbp"]].sort_values("date")

df = pd.merge(gas, fx, on="date", how="inner")

# Convert TTF from EUR/MWh into GBP/MWh.
df["ttf_price_gbp_per_mwh"] = df["ttf_price_eur_per_mwh"] * df["eur_gbp"]

# NBP is already converted into GBP/MWh in the earlier script.
df["nbp_ttf_spread_gbp_per_mwh"] = (
    df["nbp_price_gbp_per_mwh"] - df["ttf_price_gbp_per_mwh"]
)

output_path = PROCESSED_DATA / "daily_barchart_nbp_ttf_nearby_with_fx_2021_2026.csv"
df.to_csv(output_path, index=False)

print("Converted TTF into GBP/MWh and calculated NBP-TTF spread")
print()
print(df[[
    "date",
    "ttf_price_eur_per_mwh",
    "eur_gbp",
    "ttf_price_gbp_per_mwh",
    "nbp_price_gbp_per_mwh",
    "nbp_ttf_spread_gbp_per_mwh"
]].head())
print()
print(df[[
    "date",
    "ttf_price_gbp_per_mwh",
    "nbp_price_gbp_per_mwh",
    "nbp_ttf_spread_gbp_per_mwh"
]].tail())
print()
print("Rows:", len(df))
print(f"Saved file to: {output_path}")

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["ttf_price_gbp_per_mwh"], label="TTF nearby £/MWh")
plt.plot(df["date"], df["nbp_price_gbp_per_mwh"], label="NBP nearby £/MWh")
plt.title("TTF and NBP Nearby Gas Futures in GBP/MWh, 2021-2026")
plt.xlabel("Date")
plt.ylabel("Price (£/MWh)")
plt.legend()
plt.tight_layout()

price_chart = OUTPUT_CHARTS / "barchart_ttf_nbp_nearby_prices_gbp_2021_2026.png"
plt.savefig(price_chart, dpi=150)

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["nbp_ttf_spread_gbp_per_mwh"])
plt.axhline(0, linewidth=1)
plt.title("NBP-TTF Nearby Futures Spread, 2021-2026")
plt.xlabel("Date")
plt.ylabel("NBP minus TTF (£/MWh)")
plt.tight_layout()

spread_chart = OUTPUT_CHARTS / "barchart_nbp_ttf_spread_gbp_2021_2026.png"
plt.savefig(spread_chart, dpi=150)

print(f"Saved price chart to: {price_chart}")
print(f"Saved spread chart to: {spread_chart}")
