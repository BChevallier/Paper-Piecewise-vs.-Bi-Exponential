"""The piecewise-linear breakpoint fit.

Separated from `05_fit_piecewise.py` so the bike pipeline
(`bike/scripts/05_fit_piecewise.py`) fits exactly the same model. `pwlf` itself
is the model; this only wraps it into a (breakpoint, RMSE%) result.

`pwlf` searches for the breakpoint with differential evolution, which starts
from random candidates, so unseeded fits move by ~0.01-0.02 s from run to
run. The optimizer is seeded with RANDOM_SEED so every run gives the same
result. The seed value itself is arbitrary.
"""

import numpy as np
import pwlf

from metrics import rmse_percent

N_SEGMENTS = 2  # i.e. exactly one breakpoint
RANDOM_SEED = 1


def fit_piecewise_breakpoint(x, y, y_reference=None):
    """Fit a 2-segment piecewise-linear model; return (breakpoint, rmse_pct).

    The model is fitted to `y`; its RMSE% is scored against `y_reference`
    (default: `y` itself). Pass the unfiltered signal as `y_reference` when
    `y` is smoothed, so fits to differently smoothed versions of the same
    data are scored against the same measurements.

    Returns (NaN, NaN) if the fit raises or doesn't return the expected
    [x0, breakpoint, x_end] triple that `pwlf.fit(2)` normally produces.
    """
    if y_reference is None:
        y_reference = y
    try:
        fit = pwlf.PiecewiseLinFit(x, y)
        # Extra keyword arguments go to scipy's differential_evolution.
        segment_boundaries = fit.fit(N_SEGMENTS, rng=RANDOM_SEED)
        if len(segment_boundaries) != 3:
            return np.nan, np.nan
        breakpoint_s = segment_boundaries[1]
        y_hat = fit.predict(x)
        return breakpoint_s, rmse_percent(y_reference, y_hat)
    except Exception:
        return np.nan, np.nan
