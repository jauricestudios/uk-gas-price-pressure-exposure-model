

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

input_path = RAW_DATA / "systemaveragepriceofgasdataset180626.xlsx"

# The real daily gas price data starts on row 5 of the Excel sheet.
gas = pd.read_excel(
    input_path,
    sheet_name="1.Daily SAP Gas",
    header=4
)

gas = gas[["Date", "SAP actual day", "SAP seven-day rolling average"]].copy()

gas = gas.rename(columns={
    "Date": "date",
    "SAP actual day": "sap_p_per_kwh",
    "SAP seven-day rolling average": "sap_7d_avg_p_per_kwh"
})

gas["date"] = pd.to_datetime(gas["date"])

gas["sap_p_per_kwh"] = pd.to_numeric(
    gas["sap_p_per_kwh"],
    errors="coerce"
)

gas["sap_7d_avg_p_per_kwh"] = pd.to_numeric(
    gas["sap_7d_avg_p_per_kwh"],
    errors="coerce"
)

# Convert p/kWh into £/MWh.
gas["sap_price_gbp_per_mwh"] = gas["sap_p_per_kwh"] * 10
gas["sap_7d_avg_gbp_per_mwh"] = gas["sap_7d_avg_p_per_kwh"] * 10

# Keep only 2026 data for this project stage.
gas_2026 = gas[gas["date"].dt.year == 2026].copy()

# Convert daily prices into weekly prices using Friday as the week-ending date.
weekly_gas = (
    gas_2026
    .set_index("date")
    .resample("W-FRI")
    .mean(numeric_only=True)
    .reset_index()
)

weekly_gas["sap_weekly_return_pct"] = (
    weekly_gas["sap_price_gbp_per_mwh"].pct_change() * 100
)

output_path = PROCESSED_DATA / "weekly_sap_gas_2026.csv"
weekly_gas.to_csv(output_path, index=False)

print("Processed ONS/National Gas SAP gas price data.")
print(f"Saved file to: {output_path}")
print()
print(weekly_gas.head(10))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly_gas["date"],
    weekly_gas["sap_price_gbp_per_mwh"],
    marker="o"
)
plt.title("Weekly GB System Average Price of Gas - 2026")
plt.xlabel("Date")
plt.ylabel("£/MWh")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_sap_gas_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")


