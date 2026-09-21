"""
Trim each cycling time-trial CPET recording to the trial itself, then low-pass
filter V'O2.

Clock correction
----------------
The spiro device clock runs *behind* real time by a per-participant offset
recorded in delay_anmedu.xlsx: a delay of 20 means the spiro reads 2:00 when
2:20 has actually elapsed. The time trial starts TRIAL_START_REAL_S into the
session in real time, so on the spiro clock it begins at
TRIAL_START_REAL_S - delay.

An earlier version of this script trimmed at 00:03:<delay>, i.e. it *added* the
delay instead of subtracting it. For participants with a large offset that
discarded up to a minute of the V'O2 onset transient — the part the kinetics
models are fitted to.

Usage:
    python filter_and_trim_data.py            # both trials
    python filter_and_trim_data.py tt1        # one trial
"""

import sys
from pathlib import Path

import pandas as pd
from scipy.signal import butter, filtfilt

REPO_ROOT = Path(__file__).resolve().parents[1]
PATH_DELAY = REPO_ROOT / "bike_data" / "raw_data" / "delay_anmedu.xlsx"
RAW_ROOT = REPO_ROOT / "bike_data" / "raw_data"
PREPARED_ROOT = REPO_ROOT / "bike_data" / "prepared_data"

TRIALS = ("tt1", "tt2")
FIRST_PARTICIPANT = 1
LAST_PARTICIPANT = 44

# Real-time offset of the trial start from the beginning of the recording.
TRIAL_START_REAL_S = 180

COLUMNS_TO_FILTER = ["V'O2"]
CUTOFF_HZ = 0.2
FILTER_ORDER = 4
MIN_POINTS_FOR_FILTER = 20


def load_delays(trial):
    """Map participant id -> spiro clock offset in seconds for one trial."""
    df = pd.read_excel(PATH_DELAY)
    return df.set_index("PID")[f"delay_cpet_{trial}"]


def trial_start_on_spiro_clock(delay_s):
    """Spiro-clock time at which the trial starts, given the device's lag."""
    return pd.Timedelta(seconds=TRIAL_START_REAL_S - delay_s)


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
    df["t_trial_s"] = (
        df["t"].dt.total_seconds() + delay_s - TRIAL_START_REAL_S
    )

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
        pid = f"p{participant:02d}"
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
    requested = sys.argv[1:] or TRIALS
    for trial in requested:
        if trial not in TRIALS:
            raise SystemExit(f"Unknown trial {trial!r}; expected one of {TRIALS}")
        run(trial)
