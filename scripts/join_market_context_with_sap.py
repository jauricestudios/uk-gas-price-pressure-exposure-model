import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

gti_path = PROCESSED_DATA / "gti_v3_lng_with_sap_2026.csv"
market_path = PROCESSED_DATA / "weekly_nbp_ttf_prices_2026.csv"

gti = pd.read_csv(gti_path)
market = pd.read_csv(market_path)

gti["date"] = pd.to_datetime(gti["date"])
market["date"] = pd.to_datetime(market["date"])

df = pd.merge(
    gti,
    market,
    on="date",
    how="inner"
)

output_path = PROCESSED_DATA / "sap_gti_nbp_ttf_market_context_2026.csv"
df.to_csv(output_path, index=False)

print("Joined SAP, GTI, NBP and TTF market context.")
print(f"Saved file to: {output_path}")
print()
print(df[[
    "date",
    "sap_price_gbp_per_mwh",
    "sap_price_change_gbp_per_mwh",
    "sap_weekly_return_pct",
    "gti_v2_storage",
    "gti_v3_lng",
    "nbp_price_gbp_per_mwh",
    "ttf_price_eur_per_mwh",
    "nbp_return_pct",
    "ttf_return_pct"
]].head(20))

drivers = [
    "gti_v2_storage",
    "gti_v3_lng",
    "nbp_change_gbp_per_mwh",
    "ttf_change_eur_per_mwh",
    "nbp_return_pct",
    "ttf_return_pct"
]

rows = []

for driver in drivers:
    rows.append({
        "driver": driver,
        "corr_with_sap_price_change": df[driver].corr(df["sap_price_change_gbp_per_mwh"]),
        "corr_with_sap_return_pct": df[driver].corr(df["sap_weekly_return_pct"])
    })

corr = pd.DataFrame(rows)
corr = corr.sort_values("corr_with_sap_return_pct", ascending=False)

corr_path = OUTPUT_TABLES / "market_context_correlation_check_2026.csv"
corr.to_csv(corr_path, index=False)

print()
print("Market context correlation check:")
print(corr)
print()
print(f"Saved correlation table to: {corr_path}")

# Chart: SAP return vs NBP and TTF returns
plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["sap_weekly_return_pct"], marker="o", label="SAP weekly return %")
plt.plot(df["date"], df["nbp_return_pct"], marker="s", label="NBP weekly return %")
plt.plot(df["date"], df["ttf_return_pct"], marker="^", label="TTF weekly return %")
plt.axhline(0, linestyle="--")
plt.title("SAP, NBP and TTF Weekly Returns - 2026")
plt.xlabel("Date")
plt.ylabel("Weekly return (%)")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "sap_nbp_ttf_weekly_returns_2026.png"
plt.savefig(chart_path, dpi=150)

print(f"Saved returns chart to: {chart_path}")

# March shock diagnostic
march = df[
    (df["date"] >= "2026-02-27")
    & (df["date"] <= "2026-03-20")
][[
    "date",
    "sap_weekly_return_pct",
    "nbp_return_pct",
    "ttf_return_pct",
    "gti_v2_storage",
    "gti_v3_lng",
    "sap_price_change_gbp_per_mwh",
    "nbp_change_gbp_per_mwh",
    "ttf_change_eur_per_mwh"
]]

march_path = OUTPUT_TABLES / "march_shock_market_context_diagnostic.csv"
march.to_csv(march_path, index=False)

print()
print("March market-context diagnostic:")
print(march)
print()
print(f"Saved March diagnostic table to: {march_path}")
