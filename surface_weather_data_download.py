import requests
import pandas as pd
import time
import calendar

'''
Purpose of code
1. Download hourly Ground Temperature Data between 11:59am and 6:59pm from data.gov.sg
2. Download minute rain data between 11am and 6:59pm from data.gov.sg
'''

# --- User Inputs ---
API_KEY = ""  # Data.gov.sg api key
rain_or_temp = "rain"  # Downloading rain or temperature data
TARGET_YEAR = 2025
TARGET_MONTHS = [11]  # Which month you want to download data for (e.g. 11 for November)
HOUR_RANGE = range(11, 19)  # Time of day that you want to download data for
TEMP_OUTPUT_FILE = "does_this_work_temp.csv"
RAIN_OUTPUT_FILE = "does_this_work_rain.csv"
API_SLEEP_INTERVAL = 0.05
temp_url = "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"
rain_url = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"


def fetch_data_for_sounding_dates(timestamp_list, api_url):
    all_rows = []

    for ts_str in timestamp_list:
        print(f"Fetching minute: {ts_str}")
        pagination_token = None

        while True:
            params = {"date": ts_str}
            if pagination_token:
                params["paginationToken"] = pagination_token

            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Error {response.status_code} at {ts_str}")
                break

            raw_data = response.json()
            data_payload = raw_data.get('data', {})

            stations_metadata = data_payload.get('stations', [])
            station_map = {s['id']: s['name'] for s in stations_metadata}

            readings_list = data_payload.get('readings', [])

            for reading_entry in readings_list:
                actual_timestamp = reading_entry.get('timestamp')
                actual_data_points = reading_entry.get('data', [])

                for point in actual_data_points:
                    sid = point.get('stationId')
                    all_rows.append({
                        "Timestamp": actual_timestamp,
                        "Station_ID": sid,
                        "Station_Name": station_map.get(sid, "Unknown"),
                        "Value": point.get('value')
                    })

            pagination_token = data_payload.get('paginationToken')
            if not pagination_token:
                break

        time.sleep(API_SLEEP_INTERVAL)

    return pd.DataFrame(all_rows)


headers = {"x-api-key": API_KEY}
if rain_or_temp == 'rain':
    target_timestamps = [
        f"{TARGET_YEAR}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
        for month in TARGET_MONTHS
        for day in range(1, calendar.monthrange(TARGET_YEAR, month)[1] + 1)
        for hour in HOUR_RANGE
        for minute in range(0, 60)
    ]
    surface_rain_df = fetch_data_for_sounding_dates(target_timestamps, rain_url)
    surface_rain_df.to_csv(RAIN_OUTPUT_FILE)
else:
    # Download data at 59th minute of each hour instead of every minute of each hour to reduce time taken to donwload
    target_timestamps = [
        f"{TARGET_YEAR}-{month:02d}-{day:02d}T{hour:02d}:59:00"
        for month in TARGET_MONTHS
        for day in range(1, calendar.monthrange(TARGET_YEAR, month)[1] + 1)
        for hour in range(8, 18)
    ]
    surface_temp_df = fetch_data_for_sounding_dates(target_timestamps, temp_url)
    surface_temp_df.to_csv(TEMP_OUTPUT_FILE)
