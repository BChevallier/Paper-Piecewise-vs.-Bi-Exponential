import pandas as pd
from scipy.signal import butter, filtfilt

# Load your treadmill_data
df = pd.read_csv("../../../treadmill_data/prepared_data/preparedTimeTrial.csv")

# Define filter parameters
sampling_rate = 1 / 5  # 1 sample every 5 seconds = 0.2 Hz
cutoff_freq = 0.04     # Desired cutoff frequency in Hz
nyquist = 0.5 * sampling_rate
normal_cutoff = cutoff_freq / nyquist

# Design the Butterworth filter
b, a = butter(N=3, Wn=normal_cutoff, btype='low', analog=False)

# Apply the filter to all columns except 'time'
filtered_df = df.copy()
data_columns = df.columns.drop('time')
for col in data_columns:
    filtered_df[col] = filtfilt(b, a, df[col])

# Optional: Save the filtered treadmill_data to a new CSV file
filtered_df.to_csv("../../treadmill_data/prepared_data/bw_filtered_4mintt.csv", index=False)