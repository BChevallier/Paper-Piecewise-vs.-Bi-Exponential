"""Step 4a of the treadmill pipeline: fit the piecewise-linear model.

For every participant and every smoothing method ("sg" = Savitzky-Golay,
"bw" = Butterworth, "cleaned" = unfiltered), fits a continuous two-segment
piecewise-linear model to the VO2-vs-time series using `pwlf`
(`PiecewiseLinFit(x, y).fit(2)` — exactly one breakpoint; see
`piecewise_model.py`), and records:

- the fitted breakpoint location (seconds into the trial), and
- the fit's RMSE as a percentage of the signal's amplitude (see
  `metrics.rmse_percent`), a rough fit-quality score comparable across
  participants.

Outputs (in `treadmill_data/breakpoints_and_modelFit_by_method/`):
- `tt4_breakpoints_piecewise.csv` — breakpoint (s) x participant x method
- `tt4_breakpoints_piecewise_rmse_pct.csv` — RMSE% x participant x method

See `06_fit_biexponential.py` for the other model this project compares
the piecewise fit against, and the top-level README for why the two
models' "breakpoints" aren't directly the same quantity.

Run from anywhere, e.g. `python code/vo2_modeling/05_fit_piecewise.py`
from the repo root.
"""

from pathlib import Path

import pandas as pd

from piecewise_model import fit_piecewise_breakpoint

REPO_ROOT = Path(__file__).resolve().parents[2]
PREPARED_DIR = REPO_ROOT / "treadmill_data" / "prepared_data"
RESULTS_DIR = REPO_ROOT / "treadmill_data" / "breakpoints_and_modelFit_by_method"

INPUT_PATHS = {
    "sg": PREPARED_DIR / "sg_filtered_4mintt.csv",
    "bw": PREPARED_DIR / "bw_filtered_4mintt.csv",
    "cleaned": PREPARED_DIR / "preparedTimeTrial.csv",
}

BREAKPOINTS_OUTPUT = RESULTS_DIR / "tt4_breakpoints_piecewise.csv"
RMSE_PCT_OUTPUT = RESULTS_DIR / "tt4_breakpoints_piecewise_rmse_pct.csv"


def main():
    data = {method: pd.read_csv(path) for method, path in INPUT_PATHS.items()}
    participants = [col for col in data["sg"].columns if col != "time"]
    methods = list(INPUT_PATHS)

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)

    for participant in participants:
        x = data["sg"]["time"].values
        for method in methods:
            y = data[method][participant].values
            bp, pct = fit_piecewise_breakpoint(x, y)
            breakpoints.loc[participant, method] = bp
            rmse_pct.loc[participant, method] = pct

    breakpoints.to_csv(BREAKPOINTS_OUTPUT)
    rmse_pct.to_csv(RMSE_PCT_OUTPUT)
    print(f"Breakpoints saved to {BREAKPOINTS_OUTPUT}")
    print(f"RMSE percentages saved to {RMSE_PCT_OUTPUT}")


if __name__ == "__main__":
    main()
