"""
Build a final project summary for the UK Gas Price Pressure and Exposure Model.

This pulls together the main Python outputs into one readable markdown file.
"""

from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_TABLES = PROJECT_DIR / "outputs" / "tables"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

summary_path = OUTPUT_TABLES / "final_project_summary.md"

commercial = pd.read_csv(OUTPUT_TABLES / "commercial_exposure_scenarios.csv")
hedge = pd.read_csv(OUTPUT_TABLES / "hedge_sensitivity_table.csv")

current_price = commercial["current_nbp_price_gbp_per_mwh"].iloc[0]
monthly_volume = commercial["monthly_gas_volume_mwh"].iloc[0]
hedge_ratio = commercial["hedge_ratio"].iloc[0]
unhedged_volume = commercial["unhedged_volume_mwh"].iloc[0]

worst = commercial.loc[commercial["commodity_cost_impact_gbp"].idxmax()]
best = commercial.loc[commercial["commodity_cost_impact_gbp"].idxmin()]

ttf_60 = hedge[
    (hedge["scenario"] == "European TTF stress")
    & (hedge["hedge_ratio"] == 0.60)
]["cost_impact_gbp"].iloc[0]

ttf_0 = hedge[
    (hedge["scenario"] == "European TTF stress")
    & (hedge["hedge_ratio"] == 0.00)
]["cost_impact_gbp"].iloc[0]

text = f"""# UK Gas Price Pressure and Exposure Model: Final Summary

## Project question

How can physical gas-system pressure, traded gas benchmarks and global LNG context be combined into a commercial exposure model for a UK gas-exposed buyer?

## Business case

The model considers a UK medium-sized food manufacturer using {monthly_volume:,.0f} MWh of gas per month.

The buyer is assumed to have {hedge_ratio:.0%} hedge cover, leaving {unhedged_volume:,.0f} MWh exposed to floating gas prices.

The latest NBP benchmark price used in the scenario model is £{current_price:.2f}/MWh.

## Python workflow

The Python pipeline cleans and combines weather, power-system, storage, LNG, SAP, NBP, TTF, JKM and FX data.

The work is split into four layers:

1. Physical gas pressure model using HDD, wind shortfall and storage.
2. Price response testing using SAP, NBP and TTF.
3. Global gas benchmark layer using NBP, TTF and JKM in £/MWh.
4. Commercial exposure scenario model for a UK buyer.

## Main modelling result

The physical Gas Tightness Index is useful as a local pressure indicator, but it does not explain short-term gas price movements as strongly as traded market benchmarks.

The NBP, TTF and JKM benchmark layer shows that UK gas prices are connected to European and global gas markets. NBP and TTF are especially closely linked, while JKM adds wider LNG-market context.

## Commercial scenario result

The largest adverse scenario is **{worst["scenario"]}**, with an estimated monthly commodity cost impact of £{worst["commodity_cost_impact_gbp"]:,.0f} at {hedge_ratio:.0%} hedge cover.

The most favourable scenario is **{best["scenario"]}**, with an estimated monthly commodity cost impact of £{best["commodity_cost_impact_gbp"]:,.0f}.

Under the European TTF stress case:

- 0% hedge cover gives an estimated cost impact of £{ttf_0:,.0f}/month.
- 60% hedge cover gives an estimated cost impact of £{ttf_60:,.0f}/month.

This shows how hedge cover reduces exposure to gas market stress.

## Commercial interpretation

A UK gas-exposed buyer should not rely only on local physical indicators such as weather, wind and storage. Those drivers matter, but traded benchmarks such as NBP and TTF carry much of the short-term price signal.

A stronger procurement workflow should combine:

- local physical gas pressure;
- NBP and TTF market pricing;
- JKM/global LNG context;
- hedge cover;
- unhedged volume;
- scenario-based cost impact.

## Limitations

This is a scenario model, not a forecast. The scenario shocks are transparent assumptions rather than estimated future prices.

The hedge calculation assumes the hedged volume is protected at the current NBP price. In reality, hedge cost depends on tenor, liquidity, execution timing and contract structure.

JKM is used as a price benchmark only because reported Barchart volume is low or zero for much of the sample.

## Final conclusion

The project shows how Python can be used to build a market-data pipeline and commercial gas exposure model. It connects physical UK gas-system indicators, traded European benchmarks and global LNG pricing into a practical scenario framework for estimating buyer cost risk.
"""

summary_path.write_text(text)

print(f"Saved final project summary to: {summary_path}")
