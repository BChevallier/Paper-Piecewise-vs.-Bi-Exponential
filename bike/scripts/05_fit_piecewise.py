"""Step 4a of the bike pipeline: fit the piecewise-linear model.

Same model and scoring as the treadmill's `05_fit_piecewise.py` (both use
`shared/piecewise_model.py`): for every participant and every
signal variant ("sg", "bw", "cleaned" = unfiltered), fits a two-segment
piecewise-linear model and records the breakpoint (s) and RMSE% (scored
against the unfiltered data for every variant).

Outputs, per trial, in `bike/results/`:
- `<trial>_piecewise_breakpoints.csv` — breakpoint (s) x participant x method
- `<trial>_piecewise_rmse_pct.csv` — RMSE% x participant x method

Usage:
    python bike/scripts/05_fit_piecewise.py        # both trials
    python bike/scripts/05_fit_piecewise.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, RESULTS_DIR, model_input_paths, requested_trials
from piecewise_model import fit_piecewise_breakpoint


def run(trial):
    input_paths = model_input_paths(trial)
    data = {method: pd.read_csv(path) for method, path in input_paths.items()}
    participants = [col for col in data["sg"].columns if col != "time"]
    methods = list(input_paths)

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)

    x = data["sg"]["time"].values
    for participant in participants:
        unfiltered = data["cleaned"][participant].values
        for method in methods:
            y = data[method][participant].values
            bp, pct = fit_piecewise_breakpoint(x, y, y_reference=unfiltered)
            breakpoints.loc[participant, method] = bp
            rmse_pct.loc[participant, method] = pct

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    breakpoints_path = RESULTS_DIR / f"{trial}_piecewise_breakpoints.csv"
    rmse_path = RESULTS_DIR / f"{trial}_piecewise_rmse_pct.csv"
    breakpoints.to_csv(breakpoints_path)
    rmse_pct.to_csv(rmse_path)
    print(f"{trial}: breakpoints saved to {breakpoints_path.relative_to(REPO_ROOT)}")
    print(f"{trial}: RMSE percentages saved to {rmse_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
