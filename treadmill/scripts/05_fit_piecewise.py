"""Step 4a of the treadmill pipeline: fit the piecewise-linear model.

For every participant and every smoothing method ("sg" = Savitzky-Golay,
"bw" = Butterworth, "cleaned" = unfiltered), fits a continuous two-segment
piecewise-linear model to the VO2-vs-time series using `pwlf`
(`PiecewiseLinFit(x, y).fit(2)` — exactly one breakpoint; see
`shared/piecewise_model.py`), and records:

- the fitted breakpoint location (seconds into the trial), and
- the fit's RMSE against the unfiltered data, as a percentage of its
  amplitude (see `metrics.rmse_percent`) — the same reference for all
  three variants, so smoothing isn't rewarded by construction.

Outputs (in `treadmill/results/`):
- `piecewise_breakpoints.csv` — breakpoint (s) x participant x method
- `piecewise_rmse_pct.csv` — RMSE% x participant x method

See `06_fit_biexponential.py` for the other model this project compares
the piecewise fit against, and the top-level README for why the two
models' "breakpoints" aren't directly the same quantity.

Run from anywhere, e.g. `python treadmill/scripts/05_fit_piecewise.py`
from the repo root.
"""

import pandas as pd

from treadmill_common import MODEL_INPUT_PATHS as INPUT_PATHS
from treadmill_common import RESULTS_DIR
from piecewise_model import fit_piecewise_breakpoint  # needs treadmill_common imported first (sys.path)

BREAKPOINTS_OUTPUT = RESULTS_DIR / "piecewise_breakpoints.csv"
RMSE_PCT_OUTPUT = RESULTS_DIR / "piecewise_rmse_pct.csv"


def main():
    data = {method: pd.read_csv(path) for method, path in INPUT_PATHS.items()}
    participants = [col for col in data["sg"].columns if col != "time"]
    methods = list(INPUT_PATHS)

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)

    for participant in participants:
        x = data["sg"]["time"].values
        unfiltered = data["cleaned"][participant].values
        for method in methods:
            y = data[method][participant].values
            bp, pct = fit_piecewise_breakpoint(x, y, y_reference=unfiltered)
            breakpoints.loc[participant, method] = bp
            rmse_pct.loc[participant, method] = pct

    breakpoints.to_csv(BREAKPOINTS_OUTPUT)
    rmse_pct.to_csv(RMSE_PCT_OUTPUT)
    print(f"Breakpoints saved to {BREAKPOINTS_OUTPUT}")
    print(f"RMSE percentages saved to {RMSE_PCT_OUTPUT}")


if __name__ == "__main__":
    main()
