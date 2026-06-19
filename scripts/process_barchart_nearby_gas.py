"""
Process Barchart Daily Nearby UK NBP and Dutch TTF gas futures data.

Daily Nearby is a rolling nearby/front-month futures benchmark. It is built from
real futures contracts, but it is not one single traded contract.

TTF is quoted in EUR/MWh.
NBP is quoted in pence/therm and is converted to £/MWh.

NBP £/MWh = (NBP pence/therm / 100) / 0.0293071
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

TTF_PATH = RAW_DATA / "barchart_ttf_daily_nearby_2021_2026.csv"
NBP_PATH = RAW_DATA / "barchart_nbp_daily_nearby_2021_2026.csv"


def clean_barchart_file(path, contract_col, price_col):
    df = pd.read_csv(path)

    df["date"] = pd.to_datetime(df["Time"], errors="coerce")

    # Remove Barchart footer rows such as:
    # "Downloaded from Barchart.com as of..."
    df = df.dropna(subset=["date"])

    df[price_col] = pd.to_numeric(df["Latest"], errors="coerce")
    df = df.dropna(subset=[price_col])

    df = df[["date", "Symbol", price_col]]
    df = df.rename(columns={"Symbol": contract_col})
    df = df.sort_values("date").reset_index(drop=True)

    return df


ttf = clean_barchart_file(
    TTF_PATH,
    contract_col="ttf_contract",
    price_col="ttf_price_eur_per_mwh",
)

nbp = clean_barchart_file(
    NBP_PATH,
    contract_col="nbp_contract",
    price_col="nbp_price_p_per_therm",
)

nbp["nbp_price_gbp_per_mwh"] = (
    nbp["nbp_price_p_per_therm"] / 100
) / 0.0293071

df = pd.merge(ttf, nbp, on="date", how="inner")

df["ttf_log_return"] = np.log(
    df["ttf_price_eur_per_mwh"] / df["ttf_price_eur_per_mwh"].shift(1)
)

df["nbp_log_return"] = np.log(
    df["nbp_price_gbp_per_mwh"] / df["nbp_price_gbp_per_mwh"].shift(1)
)

df["ttf_return_pct"] = df["ttf_log_return"] * 100
df["nbp_return_pct"] = df["nbp_log_return"] * 100

output_path = PROCESSED_DATA / "daily_barchart_nbp_ttf_nearby_2021_2026.csv"
df.to_csv(output_path, index=False)

print("Processed Barchart Daily Nearby gas futures data")
print()
print(df.head())
print()
print(df.tail())
print()
print("Rows:", len(df))
print(f"Saved file to: {output_path}")

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["ttf_price_eur_per_mwh"], label="TTF nearby EUR/MWh")
plt.plot(df["date"], df["nbp_price_gbp_per_mwh"], label="NBP nearby £/MWh")
plt.title("TTF and NBP Nearby Gas Futures Prices, 2021-2026")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "barchart_ttf_nbp_nearby_prices_2021_2026.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved chart to: {chart_path}")
