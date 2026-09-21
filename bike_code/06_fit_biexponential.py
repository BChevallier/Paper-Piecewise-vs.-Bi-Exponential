"""Step 4b of the bike pipeline: fit the bi-exponential model.

Same model, bounds and scoring as the treadmill's `06_fit_biexponential.py`
(both use `code/vo2_modeling/biexponential_model.py`): for every participant
and every signal variant ("sg", "bw", "cleaned" = unfiltered), fits the
seven-parameter bi-exponential model and records `TD2` (the slow component's
time delay, treated as this model's "breakpoint"), the RMSE% and all seven
parameters.

Outputs, per trial, in `bike_data/breakpoints_and_modelFit_by_method/`:
- `<trial>_breakpoints_biexponential.csv` — TD2 (s) x participant x method
- `<trial>_breakpoints_biexponential_rmse_pct.csv` — RMSE% x participant x method
- `<trial>_biexponential_params.csv` — all 7 fitted params x participant x
  method (columns are a (method, param) MultiIndex)

Usage:
    python bike_code/06_fit_biexponential.py        # both trials
    python bike_code/06_fit_biexponential.py tt1    # one trial
"""

import sys

import pandas as pd

from bike_common import REPO_ROOT, RESULTS_DIR, model_input_paths, requested_trials
from biexponential_model import PARAM_NAMES, fit_biexponential

TD2_INDEX = PARAM_NAMES.index("TD2")


def run(trial):
    input_paths = model_input_paths(trial)
    data = {method: pd.read_csv(path) for method, path in input_paths.items()}
    participants = [col for col in data["sg"].columns if col != "time"]
    methods = list(input_paths)

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)
    params = pd.DataFrame(
        index=participants,
        columns=pd.MultiIndex.from_product([methods, PARAM_NAMES]),
    )

    x = data["sg"]["time"].values
    for participant in participants:
        for method in methods:
            y = data[method][participant].values
            popt, pct = fit_biexponential(x, y)
            breakpoints.loc[participant, method] = popt[TD2_INDEX]
            rmse_pct.loc[participant, method] = pct
            params.loc[participant, (method,)] = popt

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "breakpoints (TD2)": (breakpoints, f"{trial}_breakpoints_biexponential.csv"),
        "RMSE percentages": (rmse_pct, f"{trial}_breakpoints_biexponential_rmse_pct.csv"),
        "full parameter fits": (params, f"{trial}_biexponential_params.csv"),
    }
    for label, (table, filename) in outputs.items():
        path = RESULTS_DIR / filename
        table.to_csv(path)
        print(f"{trial}: {label} saved to {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        run(trial)
