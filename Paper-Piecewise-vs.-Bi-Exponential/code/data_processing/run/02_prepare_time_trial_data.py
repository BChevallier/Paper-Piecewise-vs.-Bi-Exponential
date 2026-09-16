"""Step 2 of the treadmill pipeline: trim and re-index the raw VO2 time series.

Reads `treadmill_data/raw_data/timeTrial.csv` — a wide table, one row per
5-second sample and one column per participant, VO2 in L/min — and writes
`treadmill_data/prepared_data/preparedTimeTrial.csv`, keeping only the rows
that fall inside the actual 4-minute time trial and re-indexing time in
seconds from the start of the trial (t=0).

Row layout of the raw file (verified by inspection, not assumed): each
recording starts at 00:10 and samples every 5 s.
- rows 0-57   -> 00:10 through 04:55: a ~5-minute pre-trial baseline
                 recording, before the timed trial starts. Dropped.
- rows 58-106 -> 05:00 through 09:00: the 4-minute time trial itself
                 (05:00 + 240 s = 09:00). Kept.
- rows 107-120 -> 09:05 onward, ending in blank/NaN rows: trailing
                 recording after the trial ended. Dropped.
The `- 300` offset below re-zeroes time so that 05:00 (the first kept
sample, 300 s into the raw recording) becomes t=0.

The raw file also has 5 trailing columns with no header (`Unnamed: 38..42`)
- empty artifacts of the original export - which are dropped.

Run from anywhere, e.g. `python code/data_processing/run/02_prepare_time_trial_data.py`
from the repo root. This script only ever *reads* the raw CSV — it never
edits it in place.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_PATH = REPO_ROOT / "treadmill_data" / "raw_data" / "timeTrial.csv"
OUTPUT_PATH = REPO_ROOT / "treadmill_data" / "prepared_data" / "preparedTimeTrial.csv"

# Row/column ranges below are indices into the *raw* file, verified against
# its actual timestamps (see the module docstring).
PRE_TRIAL_ROWS = slice(0, 58)          # 00:10-04:55, before the trial starts
POST_TRIAL_ROWS = slice(107, 121)      # 09:05 onward, after the trial ends
TRAILING_JUNK_COLUMNS = 5              # unnamed, empty export artifacts

TRIAL_START_OFFSET_S = 300             # 05:00 in the raw recording -> t=0


def min_sec_to_seconds(timestamp: str) -> int:
    """Convert an 'mm:ss' timestamp string to whole seconds."""
    minutes, seconds = map(int, timestamp.split(":"))
    return minutes * 60 + seconds


def prepare_time_trial_data(raw_path=RAW_PATH):
    df = pd.read_csv(raw_path)

    # Drop the tail block first so the head-block row positions aren't
    # shifted by an earlier drop.
    df = df.drop(df.index[POST_TRIAL_ROWS])
    df = df.drop(df.index[PRE_TRIAL_ROWS])

    df = df.drop(columns=df.columns[-TRAILING_JUNK_COLUMNS:])

    df["time"] = df["time"].apply(min_sec_to_seconds) - TRIAL_START_OFFSET_S
    df = df.set_index("time")

    return df


if __name__ == "__main__":
    prepared = prepare_time_trial_data()
    prepared.to_csv(OUTPUT_PATH)
    print(f"Prepared time trial data saved to {OUTPUT_PATH}")
