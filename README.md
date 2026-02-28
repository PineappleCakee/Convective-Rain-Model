# Convective-Rain-Model
Simplified model of convective rain using 2025 Singapore weather data

Description of project
We apply meteorlogical concepts CAPE and CIN to model convective rain in Singapore using sounding data from the NOAA IGRA database and rainfall and ground temperature data from data.gov.sg.
The end result in a GLM that predicts whether rain will occur given a set of sounding and ground temperature data.=

Run in the following order
1. Surface_weather_data_download.py to retrieve data from data.gov.sg. Sample of how your download should look are in the "Weather Data" foler.
2. The downloaded data is inputs for weather_data_calculations.py, which will output data for weather_forecast_model.py.
3. weather_forecast_model.py contains the GLM which can be used to make predictions on sounding data.

IGRA Data downloaded from https://www.ncei.noaa.gov/products/weather-balloon/integrated-global-radiosonde-archive
