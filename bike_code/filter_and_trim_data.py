"""
Supplementary 1 Hz export: trim each cycling time-trial CPET recording to the
trial itself and add a low-pass filtered V'O2 column, one CSV per participant
in `bike_data/prepared_data/<trial>/`.

Not part of the numbered pipeline — the models are fitted to the 5-second
tables built by `02_prepare_time_trial_data.py`. Kept as a per-second,
all-channels view of each trial for inspection. The clock correction is the
shared one in `bike_common.py`.

Usage:
    python bike_code/filter_and_trim_data.py            # both trials
    python bike_code/filter_and_trim_data.py tt1        # one trial
"""

import sys

import pandas as pd
from scipy.signal import butter, filtfilt

from bike_common import (
    FIRST_PARTICIPANT,
    LAST_PARTICIPANT,
    PREPARED_ROOT,
    RAW_ROOT,
    REPO_ROOT,
    load_delays,
    participant_id,
    requested_trials,
    seconds_since_trial_start,
    trial_start_on_spiro_clock,
)

COLUMNS_TO_FILTER = ["V'O2"]
CUTOFF_HZ = 0.2
FILTER_ORDER = 4
MIN_POINTS_FOR_FILTER = 20


def lowpass(series, fs):
    b, a = butter(FILTER_ORDER, CUTOFF_HZ, btype="low", fs=fs)
    return filtfilt(b, a, series)


def process_participant(raw_path, delay_s):
    """Trim one recording to the trial and add filtered V'O2. None if unusable."""
    df = pd.read_csv(raw_path)
    df["t"] = pd.to_timedelta(df["t"])

    df = df[df["t"] > trial_start_on_spiro_clock(delay_s)].copy()
    if df.empty:
        return None, "no data after trial start"

    # Seconds since trial start, on the corrected (real-time) clock.
    df["t_trial_s"] = seconds_since_trial_start(df["t"], delay_s)

    df = df.set_index("t")

    dt = df.index.to_series().diff().median()
    if pd.isna(dt) or dt.total_seconds() == 0:
        return None, "could not determine sampling frequency"

    fs = 1 / dt.total_seconds()
    if CUTOFF_HZ >= fs / 2:
        return None, f"cutoff {CUTOFF_HZ} Hz too high for fs {fs:.3f} Hz"

    for col in COLUMNS_TO_FILTER:
        if col not in df.columns:
            return None, f"column {col} not found"

        # Filter a cleaned copy; the recorded column is left untouched.
        signal = pd.to_numeric(df[col], errors="coerce").interpolate(
            limit_direction="both"
        )
        if signal.notna().sum() < MIN_POINTS_FOR_FILTER:
            return None, f"not enough valid points in {col}"

        df[col + "_filtered"] = lowpass(signal, fs)

    return df, None


def run(trial):
    delays = load_delays(trial)
    output_dir = PREPARED_ROOT / trial
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for participant in range(FIRST_PARTICIPANT, LAST_PARTICIPANT + 1):
        pid = participant_id(participant)
        raw_path = RAW_ROOT / trial / f"{trial}_{pid}.csv"
        if not raw_path.exists():
            continue

        delay_s = delays.get(participant)
        if pd.isna(delay_s):
            print(f"{trial} {pid}: no delay recorded, skipped")
            continue

        df, error = process_participant(raw_path, delay_s)
        if df is None:
            print(f"{trial} {pid}: {error}")
            continue

        output_path = output_dir / f"{trial}_{pid}.csv"
        df.to_csv(output_path)
        written += 1
        print(
            f"{trial} {pid}: delay {delay_s:.0f}s, "
            f"trial starts {trial_start_on_spiro_clock(delay_s)} on spiro clock, "
            f"{len(df)} rows -> {output_path.relative_to(REPO_ROOT)}"
        )

    print(f"{trial}: wrote {written} files\n")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
