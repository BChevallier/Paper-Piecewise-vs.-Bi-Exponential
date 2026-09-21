"""The piecewise-linear breakpoint fit.

Separated from `05_fit_piecewise.py` so the bike pipeline
(`bike/scripts/05_fit_piecewise.py`) fits exactly the same model. `pwlf` itself
is the model; this wraps it into a (parameters, RMSE%) result.

Parameters, in PARAM_NAMES order:

- `breakpoint`: time (s) of the junction between the two segments.
- `slope1`, `intercept1`: the first segment's line, VO2 = intercept1 +
  slope1 * t (L/min per s, L/min).
- `slope2`, `intercept2`: the second segment's line. `intercept2` is where
  that line, extended back, crosses t = 0; it is not a VO2 value the
  response actually passes through. The fit is continuous, so the two lines
  meet at the breakpoint: intercept2 is determined by the other four.

`pwlf` searches for the breakpoint with differential evolution, which starts
from random candidates, so unseeded fits move by ~0.01-0.02 s from run to
run. The optimizer is seeded with RANDOM_SEED so every run gives the same
result. The seed value itself is arbitrary.
"""

import numpy as np
import pandas as pd
import pwlf

from metrics import rmse_percent

N_SEGMENTS = 2  # i.e. exactly one breakpoint
RANDOM_SEED = 1

PARAM_NAMES = ["breakpoint", "slope1", "intercept1", "slope2", "intercept2"]


def fit_piecewise(x, y, y_reference=None):
    """Fit a 2-segment piecewise-linear model; return (params, rmse_pct).

    `params` is a length-5 array in PARAM_NAMES order. The model is fitted to
    `y`; its RMSE% is scored against `y_reference` (default: `y` itself).
    Pass the unfiltered signal as `y_reference` when `y` is smoothed, so fits
    to differently smoothed versions of the same data are scored against the
    same measurements.

    Returns (all-NaN array, NaN) if the fit raises or doesn't return the
    expected [x0, breakpoint, x_end] triple that `pwlf.fit(2)` normally
    produces.
    """
    failed = np.full(len(PARAM_NAMES), np.nan), np.nan
    if y_reference is None:
        y_reference = y
    try:
        fit = pwlf.PiecewiseLinFit(x, y)
        # Extra keyword arguments go to scipy's differential_evolution.
        segment_boundaries = fit.fit(N_SEGMENTS, rng=RANDOM_SEED)
        if len(segment_boundaries) != 3:
            return failed
        params = np.array([
            segment_boundaries[1],
            fit.slopes[0], fit.intercepts[0],
            fit.slopes[1], fit.intercepts[1],
        ])
        y_hat = fit.predict(x)
        return params, rmse_percent(y_reference, y_hat)
    except Exception:
        return failed


def piecewise_fit_tables(data):
    """Fit the piecewise model for every participant and method.

    `data` maps method ("sg", "bw", "cleaned") to a wide table: `time` plus
    one VO2 column per participant; "cleaned" (unfiltered) is the reference
    every fit is scored against. Returns a dict of output tables, keyed by
    the name each arm's step 05 saves them under:

    - piecewise_breakpoints: breakpoint per participant x method
    - piecewise_rmse_pct: RMSE% per participant x method
    - piecewise_params: all PARAM_NAMES, (method, param) columns
    """
    methods = list(data)
    participants = [col for col in data["cleaned"].columns if col != "time"]
    x = data["cleaned"]["time"].values

    breakpoints = pd.DataFrame(index=participants, columns=methods)
    rmse_pct = pd.DataFrame(index=participants, columns=methods)
    params = pd.DataFrame(
        index=participants, columns=pd.MultiIndex.from_product([methods, PARAM_NAMES])
    )

    for participant in participants:
        unfiltered = data["cleaned"][participant].values
        for method in methods:
            y = data[method][participant].values
            popt, pct = fit_piecewise(x, y, y_reference=unfiltered)
            breakpoints.loc[participant, method] = popt[0]
            rmse_pct.loc[participant, method] = pct
            params.loc[participant, (method,)] = popt

    return {
        "piecewise_breakpoints": breakpoints,
        "piecewise_rmse_pct": rmse_pct,
        "piecewise_params": params,
    }
