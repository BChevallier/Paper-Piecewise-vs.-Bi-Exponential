"""Step 1 of the treadmill pipeline: clean the per-participant summary table.

Reads `treadmill_data/raw_data/generalData.csv` (one row per participant,
see `treadmill_data/raw_data/0-raw_data-overview.md` for the full column
dictionary) and writes `treadmill_data/prepared_data/preparedGeneralData.csv`
with:

- only the columns this project's downstream scripts actually use kept
  (the other physiological/performance covariates in the raw file feed the
  paper's statistics outside this repo, and are left untouched in the raw
  file for anyone who wants them);
- `o2_intercept_y` / `o2_slope_y` converted from mL to L;
- `o2_slope_y` re-expressed as (L O2/min) per (m/s) instead of per (km/h)
  (multiply by 3.6, since 1 km/h = 1/3.6 m/s);
- a derived `speedTT4` column: each participant's average running speed
  (m/s) over the 4-minute time trial, computed from the distance covered
  (`tt4_d`, in meters) divided by the trial duration (240 s). `tt4_d`
  itself is dropped afterwards since only the derived speed is used later.

Run from anywhere, e.g. `python code/data_processing/run/01_prepare_general_data.py`
from the repo root. This script only ever *reads* the raw CSV — it never
edits it in place.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_PATH = REPO_ROOT / "treadmill_data" / "raw_data" / "generalData.csv"
OUTPUT_PATH = REPO_ROOT / "treadmill_data" / "prepared_data" / "preparedGeneralData.csv"

# Columns actually consumed downstream (currently by 07_plot_participants.py,
# which uses o2_intercept_y/o2_slope_y/speedTT4 to draw each participant's
# "expected" steady-state VO2 line). The remaining columns are kept because
# they're part of the paper's broader participant-level analysis, which
# isn't otherwise reproduced by this repo's scripts.
COLUMNS_TO_KEEP = [
    "ID", "o2_intercept_y", "o2_slope_y", "tt4_d",
    "vo2_max_abs", "body_mass", "D", "cs", "t_100", "cmj", "mss",
]

TIME_TRIAL_DURATION_S = 240  # the time trial is a fixed 4 minutes


def mL_to_L(x):
    return x / 1_000


def per_kmh_to_per_ms(x):
    """Convert a rate expressed per (km/h) to the same rate per (m/s)."""
    return x * 3.6


def distance_to_average_speed(distance_m, duration_s=TIME_TRIAL_DURATION_S):
    return distance_m / duration_s


def prepare_general_data(raw_path=RAW_PATH):
    df = pd.read_csv(raw_path)[COLUMNS_TO_KEEP]

    df["o2_intercept_y"] = df["o2_intercept_y"].apply(mL_to_L)
    df["o2_slope_y"] = df["o2_slope_y"].apply(mL_to_L).apply(per_kmh_to_per_ms)
    df["speedTT4"] = df["tt4_d"].apply(distance_to_average_speed)
    df = df.drop(columns=["tt4_d"])

    return df


if __name__ == "__main__":
    prepared = prepare_general_data()
    prepared.to_csv(OUTPUT_PATH)
    print(f"Prepared general data saved to {OUTPUT_PATH}")
