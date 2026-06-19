from pathlib import Path
import pandas as pd
import requests

RAW = Path("energy_pricing_model/data/raw")
PROCESSED = Path("energy_pricing_model/data/processed")

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)


def save_csv_from_url(url: str, output_path: Path) -> None:
    """
    Download a CSV file from a public URL and save it locally.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def download_open_meteo_oxford(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Download hourly historical temperature data for Oxford.
    Oxford is used as a simple GB weather proxy for the first build.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": 51.7520,
        "longitude": -1.2577,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m",
        "timezone": "Europe/London",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()["hourly"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df = df.rename(columns={"temperature_2m": "temperature_c"})

    return df


def main() -> None:
    weather = download_open_meteo_oxford("2026-01-01", "2026-06-16")
    weather.to_csv(RAW / "open_meteo_oxford_hourly_2026.csv", index=False)

    daily_weather = (
        weather
        .assign(date=weather["time"].dt.date)
        .groupby("date", as_index=False)
        .agg(avg_temperature_c=("temperature_c", "mean"))
    )

    daily_weather.to_csv(PROCESSED / "weather_daily_2026.csv", index=False)

    print("Saved weather data.")
    print(daily_weather.head())


if __name__ == "__main__":
    main()
