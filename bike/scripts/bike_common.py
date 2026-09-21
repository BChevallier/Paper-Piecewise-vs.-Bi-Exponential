"""Paths, trial selection and the spiro clock correction shared by the bike scripts.

Importing this module also puts `shared/` (`smoothing.py`, `metrics.py`,
`piecewise_model.py`, `biexponential_model.py`) on `sys.path`, so the bike
steps smooth and fit with exactly the same code as the treadmill steps
rather than a copy of it.

Clock correction
----------------
The spiro device clock runs *behind* real time by a per-participant offset
recorded in delay_anmedu.xlsx: a delay of 20 means the spiro reads 2:00 when
2:20 has actually elapsed. The time trial starts TRIAL_START_REAL_S into the
session in real time, so on the spiro clock it begins at
TRIAL_START_REAL_S - delay. Adding the delay instead (an earlier version did)
discards the start of the V'O2 onset transient — the part the models fit.
"""

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_DIR = REPO_ROOT / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

BIKE = REPO_ROOT / "bike"
RAW_DIR = BIKE / "data" / "raw"
CPET_EXPORTS_DIR = RAW_DIR / "cpet_exports"
PATH_DELAY = RAW_DIR / "delay_anmedu.xlsx"
CONVERTED_DIR = BIKE / "data" / "converted"
PREPARED_DIR = BIKE / "data" / "prepared"
RESULTS_DIR = BIKE / "results"
FIGURES_DIR = BIKE / "figures"

TRIALS = ("tt1", "tt2")
FIRST_PARTICIPANT = 1
LAST_PARTICIPANT = 44

# Real-time offset of the trial start from the beginning of the recording.
TRIAL_START_REAL_S = 180
# Both time trials are 4-minute efforts, like the treadmill trial.
TRIAL_DURATION_S = 240


def participant_id(participant):
    return f"p{participant:02d}"


def load_delays(trial):
    """Map participant number -> spiro clock offset in seconds for one trial."""
    df = pd.read_excel(PATH_DELAY)
    return df.set_index("PID")[f"delay_cpet_{trial}"]


def trial_start_on_spiro_clock(delay_s):
    """Spiro-clock time at which the trial starts, given the device's lag."""
    return pd.Timedelta(seconds=TRIAL_START_REAL_S - delay_s)


def seconds_since_trial_start(spiro_time, delay_s):
    """Convert spiro-clock timedeltas to seconds since trial start, real time."""
    return spiro_time.dt.total_seconds() + delay_s - TRIAL_START_REAL_S


def requested_trials(argv):
    """Trials named on the command line, or all of them if none were."""
    requested = argv[1:] or TRIALS
    for trial in requested:
        if trial not in TRIALS:
            raise SystemExit(f"Unknown trial {trial!r}; expected one of {TRIALS}")
    return requested


# One wide table per trial and signal variant: a `time` column plus one V'O2
# column per participant, the same layout as the treadmill prepared data.
def converted_path(trial, pid):
    """Per-second CSV for one participant and trial, from 01_xml_to_csv.py."""
    return CONVERTED_DIR / trial / f"{trial}_{pid}.csv"


def prepared_path(trial):
    return PREPARED_DIR / f"{trial}_time_trial.csv"


def sg_filtered_path(trial):
    return PREPARED_DIR / f"{trial}_time_trial_sg_filtered.csv"


def bw_filtered_path(trial):
    return PREPARED_DIR / f"{trial}_time_trial_bw_filtered.csv"


def model_input_paths(trial):
    """The three signal variants both models are fitted to, keyed by method."""
    return {
        "sg": sg_filtered_path(trial),
        "bw": bw_filtered_path(trial),
        "cleaned": prepared_path(trial),
    }
