import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

'''
Purpose of code
1. Fit a Binomial GLM with whether it rained as the dependant variable and
CIN, CAPE, and meeting of convective temperature as the predictors
2. Diagnose the predictive ability of the GLM using a confusion matrix
(Currently commented out) 3. Plot a diagram to show how ground temperature and CIN relate to whether it rains
'''

# Inputs
out_of_sample_month = 4  # Month to reserve for confusion matrix to do out-of-sample testing
input_data = "Combined_2025.csv"  # Exported csv from weather_data_calculation.py
rain_threshold = 2.5  # Threshold for precipitation before considering it "rain"
# -------

df = pd.read_csv(input_data)  # Input the export from weather_data_calculation.py
df['Date'] = pd.to_datetime(df['Date'])
df = df[df['Hour_UTC'] != 0]  # Use 12pm sounding data for model (data has 12pm and 12 am data)
df['rained'] = (df['Observed Rain'] > rain_threshold).astype(int)
df_in_sample = df[df['Date'].dt.month != out_of_sample_month]

model = smf.glm(
    formula="rained ~ CAPE_Jkg + Temp_Deficit_Met + CIN_Jkg",
    data=df_in_sample,
    family=sm.families.Binomial()
).fit()

print(model.summary())

# Model out of sample testing
out_of_sample_df = df[df['Date'].dt.month == out_of_sample_month]
out_of_sample_df['predicted_prob'] = model.predict(out_of_sample_df)
out_of_sample_df['predicted_rained'] = (out_of_sample_df['predicted_prob'] > 0.5).astype(int)

cm = confusion_matrix(out_of_sample_df['rained'], out_of_sample_df['predicted_rained'])
print(classification_report(out_of_sample_df['rained'], out_of_sample_df['predicted_rained']))

'''
# For testing model under specific CAPE, CIN, and Temp_deficit_met
new_data = pd.DataFrame({
    'cape': [1000],
    'cin': [-100],
    'Temp_Deficit_Met': [1]
})
predicted_prob = model.predict(new_data)
print(predicted_prob)
'''

'''
# Plot CIN against Difference between max temperature and Convective Temperature
df_in_sample = df_in_sample.copy()
df_in_sample['Temp_Distance'] = df_in_sample['Observed max temperature'] - df_in_sample['Convective_Temp_C']

fig, ax = plt.subplots(figsize=(10, 7))

colors = {0: 'steelblue', 1: 'tomato'}
labels = {0: 'No Rain (≤ 2.5mm)', 1: 'Rain (> 2.5mm)'}

for rained_val, group in df_in_sample.groupby('rained'):
    ax.scatter(
        group['CAPE_Jkg'],
        group['Temp_Distance'],
        c=colors[rained_val],
        label=labels[rained_val],
        alpha=0.6,
        edgecolors='white',
        linewidths=0.3,
        s=50
    )

ax.set_xlabel('CAPE (J/kg)', fontsize=12)
ax.set_ylabel('Observed Max Temp − Convective Temp (°C)', fontsize=12)
ax.set_title('CAPE vs Temperature Distance from Convective Temp', fontsize=14)
ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.6, label='Convective Threshold (0°C)')
ax.legend(title='Rained', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.4)
ax.set_ylim(-10, 10)
plt.tight_layout()
plt.show()
'''
