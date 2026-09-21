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
- `piecewise_params.csv` — breakpoint, both segments' slopes and
  intercepts x participant x method (columns are a (method, param)
  MultiIndex; see `shared/piecewise_model.py`)

See `06_fit_biexponential.py` for the other model this project compares
the piecewise fit against, and the top-level README for why the two
models' "breakpoints" aren't directly the same quantity.

Run from anywhere, e.g. `python treadmill/scripts/05_fit_piecewise.py`
from the repo root.
"""

import pandas as pd

from treadmill_common import MODEL_INPUT_PATHS as INPUT_PATHS
from treadmill_common import RESULTS_DIR
from piecewise_model import piecewise_fit_tables  # needs treadmill_common imported first (sys.path)


def main():
    data = {method: pd.read_csv(path) for method, path in INPUT_PATHS.items()}
    for name, table in piecewise_fit_tables(data).items():
        path = RESULTS_DIR / f"{name}.csv"
        table.to_csv(path)
        print(f"{name} saved to {path}")


if __name__ == "__main__":
    main()
