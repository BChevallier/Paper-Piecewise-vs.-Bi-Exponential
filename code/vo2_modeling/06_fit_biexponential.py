"""Step 4b of the treadmill pipeline: fit the bi-exponential model.

For every participant and every smoothing method ("sg" = Savitzky-Golay,
"bw" = Butterworth, "cleaned" = unfiltered), fits the seven-parameter
bi-exponential model defined in `biexponential_model.py` to the VO2-vs-time
series, and records:

- the fitted slow-component time delay `TD2` (seconds into the trial) —
  the quantity this project treats as the bi-exponential model's
  "breakpoint";
- the fit's RMSE as a percentage of the signal's amplitude (see
  `metrics.rmse_percent`);
- all seven fitted parameters.

Outputs (in `treadmill_data/breakpoints_and_modelFit_by_method/`):
- `tt4_breakpoints_biexponential.csv` — TD2 (s) x participant x method
- `tt4_breakpoints_biexponential_rmse_pct.csv` — RMSE% x participant x method
- `tt4_biexponential_params.csv` — all 7 fitted params x participant x
  method (columns are a (method, param) MultiIndex)

See `05_fit_piecewise.py` for the other model this project compares the
bi-exponential fit against, and the top-level README for why the two
models' "breakpoints" aren't directly the same quantity.

Run from anywhere, e.g. `python code/vo2_modeling/06_fit_biexponential.py`
from the repo root.
"""

from pathlib import Path

import pandas as pd

from biexponential_model import PARAM_NAMES, fit_biexponential

REPO_ROOT = Path(__file__).resolve().parents[2]
PREPARED_DIR = REPO_ROOT / "treadmill_data" / "prepared_data"
RESULTS_DIR = REPO_ROOT / "treadmill_data" / "breakpoints_and_modelFit_by_method"

INPUT_PATHS = {
    "sg": PREPARED_DIR / "sg_filtered_4mintt.csv",
    "bw": PREPARED_DIR / "bw_filtered_4mintt.csv",
    "cleaned": PREPARED_DIR / "preparedTimeTrial.csv",
}

BREAKPOINTS_OUTPUT = RESULTS_DIR / "tt4_breakpoints_biexponential.csv"
RMSE_PCT_OUTPUT = RESULTS_DIR / "tt4_breakpoints_biexponential_rmse_pct.csv"
PARAMS_OUTPUT = RESULTS_DIR / "tt4_biexponential_params.csv"

TD2_INDEX = PARAM_NAMES.index("TD2")


def main():
    data = {method: pd.read_csv(path) for method, path in INPUT_PATHS.items()}
    participants = [col for col in data["sg"].columns if col != "time"]
    methods = list(INPUT_PATHS)

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)
    params = pd.DataFrame(
        index=participants,
        columns=pd.MultiIndex.from_product([methods, PARAM_NAMES]),
    )

    for participant in participants:
        x = data["sg"]["time"].values
        for method in methods:
            y = data[method][participant].values
            popt, pct = fit_biexponential(x, y)
            breakpoints.loc[participant, method] = popt[TD2_INDEX]
            rmse_pct.loc[participant, method] = pct
            params.loc[participant, (method,)] = popt

    breakpoints.to_csv(BREAKPOINTS_OUTPUT)
    rmse_pct.to_csv(RMSE_PCT_OUTPUT)
    params.to_csv(PARAMS_OUTPUT)
    print(f"Breakpoints (TD2) saved to {BREAKPOINTS_OUTPUT}")
    print(f"RMSE percentages saved to {RMSE_PCT_OUTPUT}")
    print(f"Full parameter fits saved to {PARAMS_OUTPUT}")


if __name__ == "__main__":
    main()
