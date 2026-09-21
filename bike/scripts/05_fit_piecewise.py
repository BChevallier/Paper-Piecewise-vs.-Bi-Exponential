"""Step 4a of the bike pipeline: fit the piecewise-linear model.

Same model and scoring as the treadmill's `05_fit_piecewise.py` (both use
`shared/piecewise_model.py`): for every participant and every
signal variant ("sg", "bw", "cleaned" = unfiltered), fits a two-segment
piecewise-linear model and records the breakpoint (s) and RMSE% (scored
against the unfiltered data for every variant).

Outputs, per trial, in `bike/results/`:
- `<trial>_piecewise_breakpoints.csv` — breakpoint (s) x participant x method
- `<trial>_piecewise_rmse_pct.csv` — RMSE% x participant x method
- `<trial>_piecewise_params.csv` — breakpoint, both segments' slopes and
  intercepts x participant x method (columns are a (method, param)
  MultiIndex; see `shared/piecewise_model.py`)

Usage:
    python bike/scripts/05_fit_piecewise.py        # both trials
    python bike/scripts/05_fit_piecewise.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, RESULTS_DIR, model_input_paths, requested_trials
from piecewise_model import piecewise_fit_tables


def run(trial):
    data = {method: pd.read_csv(path) for method, path in model_input_paths(trial).items()}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in piecewise_fit_tables(data).items():
        path = RESULTS_DIR / f"{trial}_{name}.csv"
        table.to_csv(path)
        print(f"{trial}: {name} saved to {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
