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

The science behind it.
1. Due to various reasons, the temperature at night and in the early morning gets hotter with altitude (up to a certain height called the level of free convection).
2. When the sun rises and mid-day comes, the ground absorbs a large amount of energy and heats the air above it.
3. If the air is heated (i.e. higher than the convective temperature) to a certain temperature, the air will raise past the level of free convection.
4. Past the level of free convection, the hot air no longer has to fight the temperature gradient in the inversion and continues rising and cooling. Water vapor also condenses out of the air.
5. At some point called the equilibrium point, the air temperature reaches the same level as the surroundings.
6. When enough water vapor condenses through this process, convective rain forms.

The project calculates CAPE and CIN to determine the surface temperature required to trigger this convective rain.
CAPE is a measure the amount of work done by buoyancy after an air parcel raises past the Level of Free Convection while CIN measures the amount of work required to reach the Level of Free Convection.
In other words, CAPE measures the strength of the bouyancy push the air upwards and CIN gives an indication on the amount of hot air under the level of free convection waiting to become clouds.
