"""Step 4b of the bike pipeline: fit the bi-exponential model.

Same model, bounds and scoring as the treadmill's `06_fit_biexponential.py`
(both use `shared/biexponential_model.py`): for every participant
and every signal variant ("sg", "bw", "cleaned" = unfiltered), fits the
seven-parameter bi-exponential model and records `TD2` (the slow component's
time delay, treated as this model's "breakpoint"), the RMSE% (scored
against the unfiltered data for every variant) and all seven parameters.

It also fits the mono-exponential model (`monoexponential_model.py`, the
same model without the slow component) and compares the two with AICc (see
`model_selection.py`). Where the slow component isn't supported, TD2 is not a
meaningful quantity; `<trial>_biexponential_breakpoints_selected.csv` keeps TD2
only where it is.

Outputs, per trial, in `bike/results/`:
- `<trial>_biexponential_breakpoints.csv` — TD2 (s) x participant x method
- `<trial>_biexponential_rmse_pct.csv` — RMSE% x participant x method
- `<trial>_biexponential_params.csv` — all 7 fitted params x participant x
  method (columns are a (method, param) MultiIndex)
- `<trial>_monoexponential_rmse_pct.csv`, `<trial>_monoexponential_params.csv` — the
  same for the mono-exponential model
- `<trial>_exponential_model_selection.csv` — one row per participant and method:
  RSS, AICc and BIC of both models, their differences, whether the slow
  component is supported, and which bi-exponential parameters hit a bound
- `<trial>_biexponential_breakpoints_selected.csv` — TD2 where the slow
  component is supported, empty otherwise

Usage:
    python bike/scripts/06_fit_biexponential.py        # both trials
    python bike/scripts/06_fit_biexponential.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, RESULTS_DIR, model_input_paths, requested_trials
from model_selection import exponential_fit_tables


def run(trial):
    data = {method: pd.read_csv(path) for method, path in model_input_paths(trial).items()}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in exponential_fit_tables(data).items():
        path = RESULTS_DIR / f"{trial}_{name}.csv"
        table.to_csv(path)
        print(f"{trial}: {name} saved to {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
