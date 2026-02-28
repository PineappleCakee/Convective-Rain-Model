# Convective-Rain-Model
Simplified model of convective rain using 2025 Singapore weather data

Run in the following order
1. Surface_weather_data_download.py to retrieve data from data.gov.sg. Sample of how your download should look are in the "Weather Data" foler.
2. The downloaded data is inputs for weather_data_calculations.py, which will output data for weather_forecast_model.py.
3. weather_forecast_model.py contains the GLM which can be used to make predictions on sounding data.
