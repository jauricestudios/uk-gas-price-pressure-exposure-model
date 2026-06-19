import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

nbp_path = RAW_DATA / "nbp_futures_investing_2026.csv"
ttf_path = RAW_DATA / "ttf_futures_investing_2026.csv"

nbp = pd.read_csv(nbp_path)
ttf = pd.read_csv(ttf_path)

nbp = nbp.rename(columns={
    "Date": "date",
    "Price": "nbp_price_p_per_therm"
})

ttf = ttf.rename(columns={
    "Date": "date",
    "Price": "ttf_price_eur_per_mwh"
})

nbp["date"] = pd.to_datetime(nbp["date"], dayfirst=True)
ttf["date"] = pd.to_datetime(ttf["date"], dayfirst=True)

nbp["nbp_price_p_per_therm"] = pd.to_numeric(
    nbp["nbp_price_p_per_therm"],
    errors="coerce"
)

ttf["ttf_price_eur_per_mwh"] = pd.to_numeric(
    ttf["ttf_price_eur_per_mwh"],
    errors="coerce"
)

# Convert NBP from pence/therm to £/MWh.
# 1 therm = 0.0293071 MWh.
# pence/therm -> £/MWh = (pence / 100) / 0.0293071
nbp["nbp_price_gbp_per_mwh"] = (
    nbp["nbp_price_p_per_therm"] / 100
) / 0.0293071

nbp = nbp[[
    "date",
    "nbp_price_p_per_therm",
    "nbp_price_gbp_per_mwh"
]].copy()

ttf = ttf[[
    "date",
    "ttf_price_eur_per_mwh"
]].copy()

# Sort by date before weekly aggregation.
nbp = nbp.sort_values("date")
ttf = ttf.sort_values("date")

# For traded futures prices, use weekly last available close.
weekly_nbp = (
    nbp
    .set_index("date")
    .resample("W-FRI")
    .last()
    .reset_index()
)

weekly_ttf = (
    ttf
    .set_index("date")
    .resample("W-FRI")
    .last()
    .reset_index()
)

market = pd.merge(
    weekly_nbp,
    weekly_ttf,
    on="date",
    how="inner"
)

market["nbp_change_gbp_per_mwh"] = market["nbp_price_gbp_per_mwh"].diff()
market["ttf_change_eur_per_mwh"] = market["ttf_price_eur_per_mwh"].diff()

market["nbp_return_pct"] = market["nbp_price_gbp_per_mwh"].pct_change() * 100
market["ttf_return_pct"] = market["ttf_price_eur_per_mwh"].pct_change() * 100

output_path = PROCESSED_DATA / "weekly_nbp_ttf_prices_2026.csv"
market.to_csv(output_path, index=False)

print("Processed weekly NBP and TTF prices.")
print(f"Saved file to: {output_path}")
print()
print(market.head(20))

plt.figure(figsize=(10, 5))
plt.plot(market["date"], market["nbp_price_gbp_per_mwh"], marker="o", label="NBP £/MWh")
plt.plot(market["date"], market["ttf_price_eur_per_mwh"], marker="s", label="TTF €/MWh")
plt.title("Weekly NBP and TTF Futures Prices - 2026")
plt.xlabel("Date")
plt.ylabel("Price")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_nbp_ttf_prices_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
