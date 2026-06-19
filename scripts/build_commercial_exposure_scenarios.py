"""
Build a commercial gas exposure scenario model in Python.

Purpose
-------
This script turns the market data work into a commercial decision layer.

It defines a UK gas-exposed buyer, applies market scenarios, and calculates the
impact on monthly gas cost.

This is not a price forecast. It is a transparent scenario model.

Workflow
--------
1. Read latest NBP / TTF / JKM benchmark prices.
2. Define a UK gas-exposed buyer.
3. Define scenario assumptions for weather, storage, wind, LNG and TTF stress.
4. Convert those assumptions into a scenario NBP price shock.
5. Calculate unhedged volume and cost impact.
6. Save a scenario table and analyst note.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "processed" / "daily_global_gas_prices_gbp_2021_2026.csv"

OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"

OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# 1. Load latest market data
# ---------------------------------------------------------------------

market = pd.read_csv(DATA_PATH, parse_dates=["date"])
market = market.sort_values("date").reset_index(drop=True)

latest = market.dropna(subset=["nbp_price_gbp_per_mwh"]).iloc[-1]

latest_date = latest["date"]
current_nbp_price = latest["nbp_price_gbp_per_mwh"]
current_ttf_price = latest["ttf_price_gbp_per_mwh"]
current_jkm_price = latest["jkm_price_gbp_per_mwh"]

latest_nbp_ttf_spread = current_nbp_price - current_ttf_price
latest_jkm_nbp_spread = current_jkm_price - current_nbp_price


# ---------------------------------------------------------------------
# 2. Define the buyer
# ---------------------------------------------------------------------

buyer = {
    "buyer_name": "UK medium-sized food manufacturer",
    "monthly_gas_volume_mwh": 10_000,
    "hedge_ratio": 0.60,
    "hedge_price_gbp_per_mwh": current_nbp_price,
    "non_commodity_cost_gbp_per_mwh": 8.00,
    "risk_premium_gbp_per_mwh": 2.00,
}

monthly_volume = buyer["monthly_gas_volume_mwh"]
hedge_ratio = buyer["hedge_ratio"]
hedge_price = buyer["hedge_price_gbp_per_mwh"]

hedged_volume = monthly_volume * hedge_ratio
unhedged_volume = monthly_volume * (1 - hedge_ratio)


# ---------------------------------------------------------------------
# 3. Scenario assumptions
# ---------------------------------------------------------------------
# Pressure scores are deliberately simple and editable.
#
#  0.0 = neutral
#  1.0 = strong upward pressure
# -1.0 = strong downward pressure
#
# The weights convert each driver into percentage-point price pressure.
# These are scenario assumptions, not estimated causal coefficients.

driver_weights = {
    "weather_pressure": 3.0,
    "storage_pressure": 4.0,
    "wind_shortfall_pressure": 2.0,
    "lng_pressure": 5.0,
    "ttf_market_pressure": 10.0,
}

scenarios = pd.DataFrame([
    {
        "scenario": "Base case",
        "description": "Normal market conditions with no additional stress.",
        "weather_pressure": 0.00,
        "storage_pressure": 0.00,
        "wind_shortfall_pressure": 0.00,
        "lng_pressure": 0.00,
        "ttf_market_pressure": 0.00,
    },
    {
        "scenario": "Tight winter",
        "description": "Colder weather, lower storage comfort and some wind shortfall.",
        "weather_pressure": 1.00,
        "storage_pressure": 0.75,
        "wind_shortfall_pressure": 0.50,
        "lng_pressure": 0.25,
        "ttf_market_pressure": 0.50,
    },
    {
        "scenario": "LNG stress",
        "description": "JKM/LNG market tightens and Europe has to compete harder for cargoes.",
        "weather_pressure": 0.25,
        "storage_pressure": 0.25,
        "wind_shortfall_pressure": 0.00,
        "lng_pressure": 1.00,
        "ttf_market_pressure": 0.75,
    },
    {
        "scenario": "European TTF stress",
        "description": "Continental European gas stress pushes TTF higher relative to UK NBP.",
        "weather_pressure": 0.25,
        "storage_pressure": 0.50,
        "wind_shortfall_pressure": 0.25,
        "lng_pressure": 0.50,
        "ttf_market_pressure": 1.00,
    },
    {
        "scenario": "Weak demand",
        "description": "Mild weather, comfortable storage and weaker demand reduce gas price pressure.",
        "weather_pressure": -0.75,
        "storage_pressure": -0.50,
        "wind_shortfall_pressure": -0.50,
        "lng_pressure": -0.25,
        "ttf_market_pressure": -0.50,
    },
])


def calculate_price_shock(row):
    shock = 0
    for driver, weight in driver_weights.items():
        shock += row[driver] * weight
    return shock


scenarios["price_shock_pct"] = scenarios.apply(calculate_price_shock, axis=1)

scenarios["scenario_nbp_price_gbp_per_mwh"] = (
    current_nbp_price * (1 + scenarios["price_shock_pct"] / 100)
)


# ---------------------------------------------------------------------
# 4. Exposure calculation
# ---------------------------------------------------------------------

base_price = current_nbp_price

base_commodity_cost = (
    hedged_volume * hedge_price
    + unhedged_volume * base_price
)

base_all_in_cost = base_commodity_cost + monthly_volume * (
    buyer["non_commodity_cost_gbp_per_mwh"]
    + buyer["risk_premium_gbp_per_mwh"]
)

scenario_commodity_cost = (
    hedged_volume * hedge_price
    + unhedged_volume * scenarios["scenario_nbp_price_gbp_per_mwh"]
)

scenario_all_in_cost = scenario_commodity_cost + monthly_volume * (
    buyer["non_commodity_cost_gbp_per_mwh"]
    + buyer["risk_premium_gbp_per_mwh"]
)

scenarios["buyer_name"] = buyer["buyer_name"]
scenarios["monthly_gas_volume_mwh"] = monthly_volume
scenarios["hedge_ratio"] = hedge_ratio
scenarios["hedged_volume_mwh"] = hedged_volume
scenarios["unhedged_volume_mwh"] = unhedged_volume
scenarios["current_nbp_price_gbp_per_mwh"] = current_nbp_price
scenarios["hedge_price_gbp_per_mwh"] = hedge_price

scenarios["base_commodity_cost_gbp"] = base_commodity_cost
scenarios["scenario_commodity_cost_gbp"] = scenario_commodity_cost
scenarios["commodity_cost_impact_gbp"] = (
    scenarios["scenario_commodity_cost_gbp"] - base_commodity_cost
)

scenarios["base_all_in_cost_gbp"] = base_all_in_cost
scenarios["scenario_all_in_cost_gbp"] = scenario_all_in_cost
scenarios["all_in_cost_impact_gbp"] = (
    scenarios["scenario_all_in_cost_gbp"] - base_all_in_cost
)

scenarios["effective_commodity_price_gbp_per_mwh"] = (
    scenarios["scenario_commodity_cost_gbp"] / monthly_volume
)

scenarios["effective_all_in_price_gbp_per_mwh"] = (
    scenarios["scenario_all_in_cost_gbp"] / monthly_volume
)


def implication(cost_impact):
    if cost_impact > 50_000:
        return "High exposure: consider increasing hedge cover or adding a risk premium."
    if cost_impact > 10_000:
        return "Moderate exposure: monitor NBP, TTF and LNG spreads closely."
    if cost_impact > 0:
        return "Small adverse impact: exposure is manageable under current hedge cover."
    if cost_impact < 0:
        return "Favourable cost move: lower prices reduce unhedged gas cost."
    return "Neutral case."


scenarios["commercial_implication"] = scenarios["commodity_cost_impact_gbp"].apply(implication)


# ---------------------------------------------------------------------
# 5. Save outputs
# ---------------------------------------------------------------------

final_columns = [
    "scenario",
    "description",
    "buyer_name",
    "monthly_gas_volume_mwh",
    "hedge_ratio",
    "hedged_volume_mwh",
    "unhedged_volume_mwh",
    "current_nbp_price_gbp_per_mwh",
    "price_shock_pct",
    "scenario_nbp_price_gbp_per_mwh",
    "base_commodity_cost_gbp",
    "scenario_commodity_cost_gbp",
    "commodity_cost_impact_gbp",
    "effective_commodity_price_gbp_per_mwh",
    "effective_all_in_price_gbp_per_mwh",
    "commercial_implication",
]

output = scenarios[final_columns]

table_path = OUTPUT_TABLES / "commercial_exposure_scenarios.csv"
processed_path = PROCESSED_DATA / "commercial_exposure_scenarios.csv"

output.to_csv(table_path, index=False)
output.to_csv(processed_path, index=False)

print("Commercial gas exposure scenario model")
print()
print(f"Latest market date: {latest_date.date()}")
print(f"Current NBP price: £{current_nbp_price:.2f}/MWh")
print(f"Current TTF price: £{current_ttf_price:.2f}/MWh")
print(f"Current JKM price: £{current_jkm_price:.2f}/MWh")
print(f"Latest NBP-TTF spread: £{latest_nbp_ttf_spread:.2f}/MWh")
print(f"Latest JKM-NBP spread: £{latest_jkm_nbp_spread:.2f}/MWh")
print()
print(output[[
    "scenario",
    "price_shock_pct",
    "scenario_nbp_price_gbp_per_mwh",
    "commodity_cost_impact_gbp",
    "commercial_implication"
]])
print()
print(f"Saved scenario table to: {table_path}")


# ---------------------------------------------------------------------
# 6. Charts
# ---------------------------------------------------------------------

plt.figure(figsize=(10, 5))
plt.bar(output["scenario"], output["commodity_cost_impact_gbp"])
plt.axhline(0, linewidth=1)
plt.title("Monthly Gas Cost Impact by Scenario")
plt.xlabel("Scenario")
plt.ylabel("Cost impact (£)")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()

cost_chart = OUTPUT_CHARTS / "commercial_exposure_cost_impact_by_scenario.png"
plt.savefig(cost_chart, dpi=150)

plt.figure(figsize=(10, 5))
plt.bar(output["scenario"], output["scenario_nbp_price_gbp_per_mwh"])
plt.axhline(current_nbp_price, linewidth=1)
plt.title("Scenario NBP Price Assumptions")
plt.xlabel("Scenario")
plt.ylabel("NBP price (£/MWh)")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()

price_chart = OUTPUT_CHARTS / "commercial_exposure_scenario_prices.png"
plt.savefig(price_chart, dpi=150)

print(f"Saved cost chart to: {cost_chart}")
print(f"Saved price chart to: {price_chart}")


# ---------------------------------------------------------------------
# 7. Analyst note
# ---------------------------------------------------------------------

largest_cost = output.loc[output["commodity_cost_impact_gbp"].idxmax()]
lowest_cost = output.loc[output["commodity_cost_impact_gbp"].idxmin()]

note = f"""# Analyst Note: UK Gas Buyer Exposure

## Business case

The model considers a {buyer["buyer_name"]} with monthly gas demand of {monthly_volume:,.0f} MWh. 
The buyer is assumed to have {hedge_ratio:.0%} hedge cover, leaving {unhedged_volume:,.0f} MWh exposed to spot or floating gas price movements.

## Market context

The latest market date in the dataset is {latest_date.date()}.

- NBP price: £{current_nbp_price:.2f}/MWh
- TTF price converted to GBP: £{current_ttf_price:.2f}/MWh
- JKM price converted to GBP: £{current_jkm_price:.2f}/MWh
- NBP-TTF spread: £{latest_nbp_ttf_spread:.2f}/MWh
- JKM-NBP spread: £{latest_jkm_nbp_spread:.2f}/MWh

## Scenario result

The largest adverse case is **{largest_cost["scenario"]}**, which creates an estimated monthly commodity cost impact of £{largest_cost["commodity_cost_impact_gbp"]:,.0f}.

The most favourable case is **{lowest_cost["scenario"]}**, which creates an estimated monthly commodity cost impact of £{lowest_cost["commodity_cost_impact_gbp"]:,.0f}.

## Commercial interpretation

The model shows that even with partial hedge cover, unhedged gas volume remains exposed to benchmark price moves. The buyer should not rely only on local physical indicators such as weather, wind and storage. The earlier Python evidence showed that traded market benchmarks, especially NBP and TTF, explain a much larger part of short-term gas price movements.

A practical procurement workflow should therefore combine:

1. local physical pressure indicators;
2. NBP and TTF benchmark movements;
3. LNG/JKM market context;
4. hedge cover and unhedged volume;
5. scenario-based cost impact.

## Limitation

This is a scenario model, not a forecast. The pressure scores and scenario weights are transparent assumptions designed for commercial stress testing. They should be reviewed against market conditions before being used for a real procurement decision.
"""

note_path = OUTPUT_TABLES / "commercial_exposure_analyst_note.md"
note_path.write_text(note)

print(f"Saved analyst note to: {note_path}")
