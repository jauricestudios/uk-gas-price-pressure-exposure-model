# Analyst Note: UK Gas Buyer Exposure

## Business case

The model considers a UK medium-sized food manufacturer with monthly gas demand of 10,000 MWh. 
The buyer is assumed to have 60% hedge cover, leaving 4,000 MWh exposed to spot or floating gas price movements.

## Market context

The latest market date in the dataset is 2026-06-18.

- NBP price: £32.99/MWh
- TTF price converted to GBP: £35.27/MWh
- JKM price converted to GBP: £39.58/MWh
- NBP-TTF spread: £-2.28/MWh
- JKM-NBP spread: £6.58/MWh

## Scenario result

The largest adverse case is **European TTF stress**, which creates an estimated monthly commodity cost impact of £20,785.

The most favourable case is **Weak demand**, which creates an estimated monthly commodity cost impact of £-15,176.

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
