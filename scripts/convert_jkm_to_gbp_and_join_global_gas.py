"""
Convert JKM LNG nearby futures into GBP/MWh and join with NBP and TTF.

Common-currency gas benchmark layer:
- NBP is already in GBP/MWh
- TTF was converted into GBP/MWh using EUR/GBP
- JKM is converted into GBP/MWh using GBP/USD

JKM conversion:
JKM is quoted in USD/MMBtu.
Earlier script converted it into USD/MWh.

Since GBP/USD means dollars per pound:

    JKM GBP/MWh = JKM USD/MWh / GBP/USD
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"

OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

jkm_path = PROCESSED_DATA / "daily_barchart_jkm_lng_nearby_2021_2026.csv"
gbpusd_path = RAW_DATA / "barchart_gbpusd_daily_2021_2026.csv"
nbp_ttf_path = PROCESSED_DATA / "daily_barchart_nbp_ttf_nearby_with_fx_2021_2026.csv"

jkm = pd.read_csv(jkm_path, parse_dates=["date"])
nbp_ttf = pd.read_csv(nbp_ttf_path, parse_dates=["date"])

fx = pd.read_csv(gbpusd_path)

fx["date"] = pd.to_datetime(fx["Time"], errors="coerce")
fx = fx.dropna(subset=["date"])

fx["gbp_usd"] = pd.to_numeric(fx["Latest"], errors="coerce")
fx = fx.dropna(subset=["gbp_usd"])

fx = fx[["date", "gbp_usd"]].sort_values("date")

jkm = pd.merge(jkm, fx, on="date", how="inner")

jkm["jkm_price_gbp_per_mwh"] = jkm["jkm_price_usd_per_mwh"] / jkm["gbp_usd"]

df = pd.merge(nbp_ttf, jkm, on="date", how="inner")

df["jkm_ttf_spread_gbp_per_mwh"] = (
    df["jkm_price_gbp_per_mwh"] - df["ttf_price_gbp_per_mwh"]
)

df["jkm_nbp_spread_gbp_per_mwh"] = (
    df["jkm_price_gbp_per_mwh"] - df["nbp_price_gbp_per_mwh"]
)

output_path = PROCESSED_DATA / "daily_global_gas_prices_gbp_2021_2026.csv"
df.to_csv(output_path, index=False)

print("Converted JKM into GBP/MWh and joined global gas benchmarks")
print()
print(df[[
    "date",
    "nbp_price_gbp_per_mwh",
    "ttf_price_gbp_per_mwh",
    "jkm_price_gbp_per_mwh",
    "jkm_ttf_spread_gbp_per_mwh",
    "jkm_nbp_spread_gbp_per_mwh"
]].head())
print()
print(df[[
    "date",
    "nbp_price_gbp_per_mwh",
    "ttf_price_gbp_per_mwh",
    "jkm_price_gbp_per_mwh",
    "jkm_ttf_spread_gbp_per_mwh",
    "jkm_nbp_spread_gbp_per_mwh"
]].tail())
print()
print("Rows:", len(df))
print(f"Saved file to: {output_path}")

corr = df[["nbp_return_pct", "ttf_return_pct", "jkm_return_pct"]].corr()
corr_path = OUTPUT_TABLES / "global_gas_daily_return_correlation_2021_2026.csv"
corr.to_csv(corr_path)

print()
print("Daily return correlation")
print(corr)
print()
print(f"Saved correlation table to: {corr_path}")

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["nbp_price_gbp_per_mwh"], label="NBP £/MWh")
plt.plot(df["date"], df["ttf_price_gbp_per_mwh"], label="TTF £/MWh")
plt.plot(df["date"], df["jkm_price_gbp_per_mwh"], label="JKM £/MWh")
plt.title("Global Gas Benchmarks in GBP/MWh, 2021-2026")
plt.xlabel("Date")
plt.ylabel("Price (£/MWh)")
plt.legend()
plt.tight_layout()

price_chart = OUTPUT_CHARTS / "global_gas_prices_gbp_2021_2026.png"
plt.savefig(price_chart, dpi=150)

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["jkm_ttf_spread_gbp_per_mwh"], label="JKM minus TTF")
plt.plot(df["date"], df["jkm_nbp_spread_gbp_per_mwh"], label="JKM minus NBP")
plt.axhline(0, linewidth=1)
plt.title("JKM Premium/Discount vs European Gas Benchmarks, 2021-2026")
plt.xlabel("Date")
plt.ylabel("Spread (£/MWh)")
plt.legend()
plt.tight_layout()

spread_chart = OUTPUT_CHARTS / "jkm_vs_europe_gas_spreads_gbp_2021_2026.png"
plt.savefig(spread_chart, dpi=150)

print(f"Saved price chart to: {price_chart}")
print(f"Saved spread chart to: {spread_chart}")
