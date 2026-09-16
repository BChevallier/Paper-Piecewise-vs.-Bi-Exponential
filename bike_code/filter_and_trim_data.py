import pandas as pd
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from pathlib import Path


PATH_DELAY = Path("../bike_data/raw_data/delay_anmedu.xlsx")
PATH_O2 = Path("../bike_data/raw_data/tt2")
OUTPUT_PATH = Path("../bike_data/prepared_data/tt2")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

df_delay = pd.read_excel(PATH_DELAY)

columns_to_filter = ["V'O2"]

cutoff = 0.2  # Hz
order = 4

for i in range(1, 45):
    participant_id = str(i).zfill(2)

    input_file = PATH_O2 / f"tt2_p{participant_id}.csv"
    output_file = OUTPUT_PATH / f"tt2_p{participant_id}.csv"

    try:
        df_o2 = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"P{participant_id} not found")
        continue

    # Convert time column
    df_o2["t"] = pd.to_timedelta(df_o2["t"])

    # Get participant-specific delay
    delay = df_delay.loc[i - 1, "delay_cpet_tt2"]

    print(f"Delay of P{participant_id}: {delay}")

    # Remove rows before/equal to delay
    df_o2 = df_o2[df_o2["t"] > pd.Timedelta(f"00:03:{delay}")].copy()

    if df_o2.empty:
        print(f"P{participant_id}: no data after delay")
        continue

    # Set t as index so sampling frequency is calculated from time
    df_o2 = df_o2.set_index("t")

    # Calculate sampling frequency from TimedeltaIndex
    dt = df_o2.index.to_series().diff().median()

    if pd.isna(dt) or dt.total_seconds() == 0:
        print(f"P{participant_id}: could not calculate sampling frequency")
        continue

    fs = 1 / dt.total_seconds()

    # Check cutoff frequency
    if cutoff >= fs / 2:
        print(
            f"P{participant_id}: cutoff {cutoff} Hz is too high for fs {fs:.3f} Hz"
        )
        continue

    b, a = butter(order, cutoff, btype="low", fs=fs)

    for col in columns_to_filter:
        if col not in df_o2.columns:
            print(f"P{participant_id}: column {col} not found")
            continue

        df_o2[col] = pd.to_numeric(df_o2[col], errors="coerce")
        df_o2[col] = df_o2[col].interpolate(limit_direction="both")

        # filtfilt needs enough valid points
        if df_o2[col].notna().sum() < 20:
            print(f"P{participant_id}: not enough data points for {col}")
            continue

        df_o2[col + "_filtered"] = filtfilt(
            b,
            a,
            df_o2[col]
        )

    # Save after filtering
    df_o2.to_csv(output_file)

    print(f"P{participant_id}: saved {output_file}")


print("Finished.")
df_o2.plot(y="V'O2_filtered")
plt.show()