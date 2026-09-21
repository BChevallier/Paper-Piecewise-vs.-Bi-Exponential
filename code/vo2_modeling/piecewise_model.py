"""The piecewise-linear breakpoint fit.

Separated from `05_fit_piecewise.py` so the bike pipeline
(`bike_code/05_fit_piecewise.py`) fits exactly the same model. `pwlf` itself
is the model; this only wraps it into a (breakpoint, RMSE%) result.
"""

import numpy as np
import pwlf

from metrics import rmse_percent

N_SEGMENTS = 2  # i.e. exactly one breakpoint


def fit_piecewise_breakpoint(x, y):
    """Fit a 2-segment piecewise-linear model; return (breakpoint, rmse_pct).

    Returns (NaN, NaN) if the fit raises or doesn't return the expected
    [x0, breakpoint, x_end] triple that `pwlf.fit(2)` normally produces.
    """
    try:
        fit = pwlf.PiecewiseLinFit(x, y)
        segment_boundaries = fit.fit(N_SEGMENTS)
        if len(segment_boundaries) != 3:
            return np.nan, np.nan
        breakpoint_s = segment_boundaries[1]
        y_hat = fit.predict(x)
        return breakpoint_s, rmse_percent(y, y_hat)
    except Exception:
        return np.nan, np.nan
