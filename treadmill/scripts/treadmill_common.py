"""Paths shared by the treadmill scripts.

Importing this module also puts `shared/` (the smoothing and model code both
arms use) on `sys.path`, so the scripts can `from smoothing import ...` etc.
Every path is resolved from this file's location, so the scripts run from any
working directory.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_DIR = REPO_ROOT / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

TREADMILL = REPO_ROOT / "treadmill"
RAW_DIR = TREADMILL / "data" / "raw"
PREPARED_DIR = TREADMILL / "data" / "prepared"
RESULTS_DIR = TREADMILL / "results"
FIGURES_DIR = TREADMILL / "figures"

RAW_GENERAL_DATA = RAW_DIR / "general_data.csv"
RAW_TIME_TRIAL = RAW_DIR / "time_trial.csv"

GENERAL_DATA = PREPARED_DIR / "general_data.csv"
TIME_TRIAL = PREPARED_DIR / "time_trial.csv"
TIME_TRIAL_SG = PREPARED_DIR / "time_trial_sg_filtered.csv"
TIME_TRIAL_BW = PREPARED_DIR / "time_trial_bw_filtered.csv"

# The three signal variants both models are fitted to, keyed by method.
# "cleaned" is the unfiltered prepared series — the no-smoothing control.
MODEL_INPUT_PATHS = {
    "sg": TIME_TRIAL_SG,
    "bw": TIME_TRIAL_BW,
    "cleaned": TIME_TRIAL,
}
