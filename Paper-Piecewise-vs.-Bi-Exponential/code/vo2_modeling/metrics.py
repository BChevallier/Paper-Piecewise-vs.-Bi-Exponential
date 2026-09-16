"""Shared fit-quality metric used by both modeling scripts.

Kept as a one-function module so the two model comparisons
(`05_fit_piecewise.py`, `06_fit_biexponential.py`) score their fits the
same way, rather than each having its own copy of the same three lines.
"""

import numpy as np


def rmse_percent(y_observed, y_predicted):
    """RMSE of a fit, expressed as a percentage of the signal's amplitude.

    Normalizing by amplitude (max - min of the observed signal) makes the
    error comparable across participants whose absolute VO2 range differs.
    Returns NaN if the observed signal is flat (amplitude 0), since a
    percentage of zero range is undefined.
    """
    y_observed = np.asarray(y_observed)
    y_predicted = np.asarray(y_predicted)

    amplitude = np.max(y_observed) - np.min(y_observed)
    if amplitude == 0:
        return np.nan

    rmse = np.sqrt(np.mean((y_observed - y_predicted) ** 2))
    return (rmse / amplitude) * 100
