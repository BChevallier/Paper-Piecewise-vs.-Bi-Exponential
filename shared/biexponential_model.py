"""The bi-exponential VO2 on-kinetics model: definition and curve-fitting.

Separated from `06_fit_biexponential.py` (which loops the fit over every
participant and file) so the model itself — the part a reader is most
likely to want to check against the paper's methods section — can be read
on its own.

Model form (seven free parameters): a constant baseline plus two
independently-delayed exponential rises, following the two-time-delay
extension to standard mono-exponential VO2 on-kinetics modeling used in
Bell et al. (2001, Exp Physiol 86(5):667-676) for characterizing the
primary/fast phase and the slow-component phase of the response
separately:

    VO2(t) = A0
             + A1 * (1 - exp(-(t - TD1)_clamped / tau1))   # fast component
             + A2 * (1 - exp(-(t - TD2)_clamped / tau2))   # slow component

where `(t - TD)_clamped = clip(t - TD, 0, 300)`, i.e. each component is
exactly zero before its own time delay and stops evolving 300 s after it
starts (well beyond the 240 s trial, so this only guards against overflow
in the optimizer, not a real physiological cutoff).

- `A0`: baseline VO2 before the response begins.
- `A1`, `tau1`, `TD1`: amplitude, time constant, and time delay of the
  fast/primary kinetics component.
- `A2`, `tau2`, `TD2`: amplitude, time constant, and time delay of the
  slower component. `TD2` is the value this project treats as the
  bi-exponential model's "breakpoint", analogous to (but not the same
  quantity as) the piecewise-linear model's breakpoint in
  `05_fit_piecewise.py` - see the top-level README for how the two are
  and aren't comparable.
"""

import numpy as np
from scipy.optimize import curve_fit

from metrics import rmse_percent

PARAM_NAMES = ["A0", "A1", "tau1", "TD1", "A2", "tau2", "TD2"]

# Lower/upper bounds passed to curve_fit, in PARAM_NAMES order. Chosen to
# keep the optimizer within physiologically plausible ranges for a 4-minute
# trial (e.g. TD2 within the trial itself) rather than fit to the data.
PARAM_BOUNDS = (
    [0, 0, 1, 0, 0, 10, 30],
    [5, 5, 100, 60, 5, 300, 240],
)

CLAMP_MAX_S = 300


def biexponential(t, A0, A1, tau1, TD1, A2, tau2, TD2):
    t = np.asarray(t)
    t1 = np.clip(t - TD1, 0, CLAMP_MAX_S)
    t2 = np.clip(t - TD2, 0, CLAMP_MAX_S)
    fast_component = A1 * (1 - np.exp(-t1 / tau1))
    slow_component = A2 * (1 - np.exp(-t2 / tau2))
    return A0 + fast_component + slow_component


def _initial_guess(y):
    """Heuristic starting point for curve_fit, in PARAM_NAMES order."""
    A0_guess = y[0]
    A1_guess = y.max() - y[0]
    tau1_guess = 30
    TD1_guess = 15
    A2_guess = A1_guess * 0.2
    tau2_guess = 100
    TD2_guess = 120
    return [A0_guess, A1_guess, tau1_guess, TD1_guess, A2_guess, tau2_guess, TD2_guess]


def fit_biexponential(x, y, y_reference=None):
    """Fit the bi-exponential model to one participant's VO2 series.

    The model is fitted to `y`; its RMSE% is scored against `y_reference`
    (default: `y` itself). Pass the unfiltered signal as `y_reference` when
    `y` is smoothed, so fits to differently smoothed versions of the same
    data are scored against the same measurements.

    Returns (params, rmse_pct) where `params` is a length-7 array in
    PARAM_NAMES order, or (all-NaN array, NaN) if the fit fails to
    converge within bounds.
    """
    if y_reference is None:
        y_reference = y
    try:
        popt, _ = curve_fit(
            biexponential, x, y,
            p0=_initial_guess(y),
            bounds=PARAM_BOUNDS,
            maxfev=10000,
        )
        y_hat = biexponential(x, *popt)
        return popt, rmse_percent(y_reference, y_hat)
    except Exception:
        return np.full(len(PARAM_NAMES), np.nan), np.nan
