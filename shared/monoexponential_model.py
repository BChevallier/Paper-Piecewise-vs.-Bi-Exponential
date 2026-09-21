"""The mono-exponential VO2 on-kinetics model: the bi-exponential without its
slow component.

    VO2(t) = A0 + A1 * (1 - exp(-(t - TD1)_clamped / tau1))

It is exactly `biexponential_model.biexponential` with A2 = 0, and uses the
same bounds for its four parameters, so the two models are nested and can be
compared directly (see `model_selection.py`). It exists as the null model for
the question "does this response have a slow component at all?".
"""

import numpy as np
from scipy.optimize import curve_fit

from biexponential_model import CLAMP_MAX_S, PARAM_BOUNDS as BIEXP_BOUNDS
from metrics import rmse_percent

PARAM_NAMES = ["A0", "A1", "tau1", "TD1"]

# The bi-exponential's bounds for the same four parameters.
PARAM_BOUNDS = (
    BIEXP_BOUNDS[0][: len(PARAM_NAMES)],
    BIEXP_BOUNDS[1][: len(PARAM_NAMES)],
)


def monoexponential(t, A0, A1, tau1, TD1):
    t = np.asarray(t)
    t1 = np.clip(t - TD1, 0, CLAMP_MAX_S)
    return A0 + A1 * (1 - np.exp(-t1 / tau1))


def _initial_guess(y):
    """Heuristic starting point for curve_fit, in PARAM_NAMES order."""
    return [y[0], y.max() - y[0], 30, 15]


def fit_monoexponential(x, y, y_reference=None):
    """Fit the mono-exponential model to one participant's VO2 series.

    Same contract as `biexponential_model.fit_biexponential`: fitted to `y`,
    RMSE% scored against `y_reference` (default `y`). Returns (params,
    rmse_pct), or (all-NaN array, NaN) if the fit fails.
    """
    if y_reference is None:
        y_reference = y
    try:
        popt, _ = curve_fit(
            monoexponential, x, y,
            p0=_initial_guess(y),
            bounds=PARAM_BOUNDS,
            maxfev=10000,
        )
        y_hat = monoexponential(x, *popt)
        return popt, rmse_percent(y_reference, y_hat)
    except Exception:
        return np.full(len(PARAM_NAMES), np.nan), np.nan
