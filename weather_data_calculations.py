import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units

'''
Purpose of code
1. Process Singapore sounding data NOAA IGRA data into a data frame
2. Calculate Convective Temperature, CIN, and CAPE implied the NOAA IGRA data
3. Process Singapore Ground temperature and rain data from data.gov.sg and combine into NOAA IGRA dataframe
4. Identify days where convective temperature is exceeded
'''

r'''
# If working directory change needed
working_directory = r"."
os.chdir(working_directory)
'''

# Inputs
sounding_data = r'Weather Data\Singapore Sounding Data 2025 NOAA IGRA.txt'  # Sounding data from NOAA IGRA
ground_temp_data = r'Weather Data\Singapore_Ground_Temp.csv'  # Ground temp data from data.gov.sg (use surface_weather_data_download.py)
rain_data = r'Weather Data\Singapore_Ground_Rain.csv'  # Rain data from data.gov.sg (use surface_weather_data_download.py)
export_filepath = 'Combined_2025.csv'
# ------------


def parse_igra_fixed_width(filepath):
    dataset = []
    current_header = None

    with open(filepath, 'r') as f:
        for line in f:
            # Header records start with '#'
            if line.startswith('#'):
                current_header = {
                    'station_id': line[1:12].strip(),
                    'year': int(line[13:17]),
                    'month': int(line[18:20]),
                    'day': int(line[21:23]),
                    'hour': int(line[24:26]),
                    'rel_time': line[27:31].strip(),
                    'num_lev': int(line[32:36])
                }
            else:
                # Extracting and handling '-9999' and 'A' or 'B' flags as NaN
                def get_val(start, end, scale=1):
                    val = line[start-1:end].strip()
                    val = ''.join(c for c in val if c.isdigit() or c == '-')
                    if not val or val == "-9999" or val == "-8888":
                        return np.nan
                    return float(val) / scale

                row = {
                    **current_header,
                    'lvl_typ1': get_val(1, 1),
                    'lvl_typ2': get_val(2, 2),
                    'etime': get_val(4, 8),
                    'pressure': get_val(10, 15),
                    'gph': get_val(17, 21),
                    'temp': get_val(23, 27, scale=10),  # Tenths of deg C
                    'rh': get_val(29, 33, scale=10),  # Tenths of %
                    'dpdp': get_val(35, 39, scale=10),  # Tenths of deg C
                    'wdir': get_val(41, 45),
                    'wspd': get_val(47, 51, scale=10)  # Tenths of m/s
                }
                dataset.append(row)

    df = pd.DataFrame(dataset)
    df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df


def calculate_stability_parameters(df):
    results = []

    # Group by unique sounding (Date and Hour)
    for (timestamp, hour), group in df.groupby(['timestamp', 'hour']):
        # MetPy requires non-NaN values for Pressure, Temp, and Dewpoint
        group = group.dropna(subset=['pressure', 'temp', 'dpdp']).sort_values('pressure', ascending=False)

        if len(group) < 10:  # Skip soundings with insufficient vertical resolution
            continue
        p = group['pressure'].values * units.pascal
        T = group['temp'].values * units.degC
        # Dewpoint = Temperature - Dewpoint Depression
        Td = (group['temp'].values - group['dpdp'].values) * units.degC

        try:
            # This follows the parcel as it rises dry-adiabatically to LCL, then moist-adiabatically
            prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
            cape, cin = mpcalc.cape_cin(p, T, Td, prof)
            lfc_p, lfc_t = mpcalc.lfc(p, T, Td, prof)
            el_p, el_t = mpcalc.el(p, T, Td, prof)
            # mpcalc.ccl returns: (CCL Pressure, CCL Temp, Convective Temp)
            p_ccl, t_ccl, t_conv = mpcalc.ccl(p, T, Td)

            results.append({
                'Date': timestamp.strftime('%Y-%m-%d'),
                'Hour_UTC': hour,
                'CAPE_Jkg': round(float(cape.magnitude), 2),
                'CIN_Jkg': round(float(cin.magnitude), 2),
                'LFC_hPa': round(float(lfc_p.to(units.hPa).magnitude), 1) if not np.isnan(lfc_p) else np.nan,
                'EL_hPa': round(float(el_p.to(units.hPa).magnitude), 1) if not np.isnan(el_p) else np.nan,
                'CCL_hPa': round(float(p_ccl.to(units.hPa).magnitude), 1) if not np.isnan(p_ccl) else np.nan,
                'Sfc_Temp_C': round(float(T[0].magnitude), 2),
                'Convective_Temp_C': round(float(t_conv.magnitude), 2),
                'Heating_Needed_C': round(float(t_conv.magnitude - T[0].magnitude), 2)
            })

        except Exception:
            # Some profiles may be too dry or stable to solve for LFC/CCL
            continue

    return pd.DataFrame(results)


df = parse_igra_fixed_width(sounding_data)
stability_results = calculate_stability_parameters(df)
station_id = 'S43' # S43 is Kim Chuan Road, which is Paya Lebar sounding station

# Figure out max Surface Temperature data for each day
df_temp = pd.read_csv(ground_temp_data)
df_temp['Date'] = pd.to_datetime(df_temp['Timestamp']).dt.strftime('%Y-%m-%d')
paya_lebar_temp = df_temp[df_temp['Station_ID'] == station_id]
daily_max_temp = paya_lebar_temp.groupby('Date')['Value'].max().reset_index()
daily_max_temp.columns = ['Date', 'Observed max temperature']
stability_results = stability_results.merge(daily_max_temp, on='Date', how='left')

# Figure out rain amount between 1000 and 1859 for each day
df_rain = pd.read_csv(rain_data)
df_rain['Date'] = pd.to_datetime(df_rain['Timestamp']).dt.strftime('%Y-%m-%d')
paya_lebar_rain = df_rain[df_rain['Station_ID'] == station_id]
daily_sum_rain = paya_lebar_rain.groupby('Date')['Value'].sum().reset_index()
daily_sum_rain.columns = ['Date', 'Observed Rain']
stability_results = stability_results.merge(daily_sum_rain, on='Date', how='left')

# Check convective rain condition, instead of True/False use 1/0 to make regression easier later
stability_results['Temp_Deficit_Met'] = (stability_results['Observed max temperature'] >= stability_results['Convective_Temp_C']).astype(int)
stability_results = stability_results[stability_results['Observed Rain'].notna()] # Remove dates with no rain data
stability_results.to_csv(export_filepath, index=False)


'''
# Plotting Temperature vs Altitude
df_midnight = df[(df['hour'] == 0) & (df['gph'] <= 2000) & (df['day'] == 1)].copy()
df_midnight['date'] = pd.to_datetime(df_midnight[['year', 'month', 'day']])
plt.figure(figsize=(10, 8))
for date, group in df_midnight.groupby('date'):
    group = group.sort_values('gph')
    plt.plot(group['temp'], group['gph'], alpha=0.6)

plt.xlabel('Temperature (°C)')
plt.ylabel('Altitude (GPH in meters)')
plt.title('Daily Temperature Profiles for Singapore (00:00 UTC)')
plt.grid(True)
plt.savefig('temperature_profiles_midnight.jpg')
'''