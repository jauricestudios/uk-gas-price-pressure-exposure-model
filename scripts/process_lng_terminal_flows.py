import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA = PROJECT_DIR / "data" / "processed"
OUTPUT_CHARTS = PROJECT_DIR / "outputs" / "charts"

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS.mkdir(parents=True, exist_ok=True)

input_path = RAW_DATA / "national_gas_lng_terminal_flows_2026.csv"

lng = pd.read_csv(input_path)

lng = lng.rename(columns={
    "Applicable For": "date",
    "Data Item": "data_item",
    "Value": "value",
    "Generated Time": "generated_time"
})

lng["date"] = pd.to_datetime(lng["date"], dayfirst=True)
lng["generated_time"] = pd.to_datetime(lng["generated_time"], dayfirst=True)
lng["value"] = pd.to_numeric(lng["value"], errors="coerce")

# Keep LNG terminal outflow items.
# This is used as a send-out / terminal supply proxy.
lng_outflow = lng[
    lng["data_item"].str.contains("Outflow", case=False, na=False)
    & lng["data_item"].str.contains("LNG Importation", case=False, na=False)
].copy()

# Keep latest published value for each gas day and data item.
lng_outflow = (
    lng_outflow
    .sort_values(["date", "data_item", "generated_time"])
    .drop_duplicates(subset=["date", "data_item"], keep="last")
)

lng_wide = (
    lng_outflow
    .pivot_table(
        index="date",
        columns="data_item",
        values="value",
        aggfunc="mean"
    )
    .reset_index()
)

lng_wide = lng_wide.rename(columns={
    "Outflow, Isle Of Grain, LNG Importation": "isle_of_grain_lng_outflow",
    "Outflow, South Hook, LNG Importation": "south_hook_lng_outflow",
    "Outflow, Dragon, LNG Importation": "dragon_lng_outflow"
})

for col in [
    "isle_of_grain_lng_outflow",
    "south_hook_lng_outflow",
    "dragon_lng_outflow"
]:
    if col not in lng_wide.columns:
        lng_wide[col] = 0

lng_wide["total_lng_outflow"] = (
    lng_wide["isle_of_grain_lng_outflow"].fillna(0)
    + lng_wide["south_hook_lng_outflow"].fillna(0)
    + lng_wide["dragon_lng_outflow"].fillna(0)
)

weekly_lng = (
    lng_wide
    .set_index("date")
    .resample("W-FRI")
    .mean(numeric_only=True)
    .reset_index()
)

# Low LNG pressure:
# higher value means LNG outflow is lower than its own sample average.
mean_lng = weekly_lng["total_lng_outflow"].mean()
std_lng = weekly_lng["total_lng_outflow"].std()

if std_lng == 0:
    weekly_lng["low_lng_sendout_pressure"] = 0
else:
    weekly_lng["low_lng_sendout_pressure"] = (
        mean_lng - weekly_lng["total_lng_outflow"]
    ) / std_lng

output_path = PROCESSED_DATA / "weekly_lng_terminal_flows_2026.csv"
weekly_lng.to_csv(output_path, index=False)

print("Processed LNG terminal flow data.")
print(f"Saved file to: {output_path}")
print()
print(weekly_lng.head(20))

plt.figure(figsize=(10, 5))
plt.plot(
    weekly_lng["date"],
    weekly_lng["total_lng_outflow"],
    marker="o"
)
plt.title("Weekly LNG Terminal Outflow - 2026")
plt.xlabel("Date")
plt.ylabel("Total LNG outflow, National Gas published units")
plt.xticks(rotation=45)
plt.tight_layout()

chart_path = OUTPUT_CHARTS / "weekly_lng_terminal_outflow_2026.png"
plt.savefig(chart_path, dpi=150)

print()
print(f"Saved chart to: {chart_path}")
