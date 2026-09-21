"""Step 4b of the treadmill pipeline: fit the bi-exponential model.

For every participant and every smoothing method ("sg" = Savitzky-Golay,
"bw" = Butterworth, "cleaned" = unfiltered), fits the seven-parameter
bi-exponential model defined in `biexponential_model.py` to the VO2-vs-time
series, and records:

- the fitted slow-component time delay `TD2` (seconds into the trial) —
  the quantity this project treats as the bi-exponential model's
  "breakpoint";
- the fit's RMSE against the unfiltered data, as a percentage of its
  amplitude (see `metrics.rmse_percent`) — the same reference for all
  three variants;
- all seven fitted parameters.

It also fits the mono-exponential model (`monoexponential_model.py`, the
same model without the slow component) and compares the two with AICc (see
`model_selection.py`). Where the slow component isn't supported, TD2 is not a
meaningful quantity; `biexponential_breakpoints_selected.csv` keeps TD2
only where it is.

Outputs (in `treadmill/results/`):
- `biexponential_breakpoints.csv` — TD2 (s) x participant x method
- `biexponential_rmse_pct.csv` — RMSE% x participant x method
- `biexponential_params.csv` — all 7 fitted params x participant x
  method (columns are a (method, param) MultiIndex)
- `monoexponential_rmse_pct.csv`, `monoexponential_params.csv` — the
  same for the mono-exponential model
- `exponential_model_selection.csv` — one row per participant and method:
  RSS, AICc and BIC of both models, their differences, whether the slow
  component is supported, and which bi-exponential parameters hit a bound
- `biexponential_breakpoints_selected.csv` — TD2 where the slow
  component is supported, empty otherwise

See `05_fit_piecewise.py` for the other model this project compares the
bi-exponential fit against, and the top-level README for why the two
models' "breakpoints" aren't directly the same quantity.

Run from anywhere, e.g. `python treadmill/scripts/06_fit_biexponential.py`
from the repo root.
"""

import pandas as pd

from treadmill_common import MODEL_INPUT_PATHS as INPUT_PATHS
from treadmill_common import RESULTS_DIR
from model_selection import exponential_fit_tables  # needs treadmill_common imported first (sys.path)


def main():
    data = {method: pd.read_csv(path) for method, path in INPUT_PATHS.items()}
    for name, table in exponential_fit_tables(data).items():
        path = RESULTS_DIR / f"{name}.csv"
        table.to_csv(path)
        print(f"{name} saved to {path}")


if __name__ == "__main__":
    main()
