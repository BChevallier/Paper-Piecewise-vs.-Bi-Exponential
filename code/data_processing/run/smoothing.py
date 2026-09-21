"""The two competing smoothing methods this project compares.

Shared by the treadmill filter steps (`03_filter_savitzky_golay.py`,
`04_filter_butterworth.py`) and their bike counterparts in `bike_code/`, so
both modalities are smoothed by the same code with the same settings.

Both functions take a wide table — a `time` column plus one VO2 column per
participant, on a fixed sample spacing — and return a smoothed copy with the
same shape; `time` is left untouched.
"""

from scipy.signal import butter, filtfilt, savgol_filter

SG_WINDOW_LENGTH = 7  # samples; must be odd and <= number of data points
SG_POLY_ORDER = 3

BW_SAMPLING_RATE_HZ = 1 / 5   # one sample every 5 s
BW_CUTOFF_FREQ_HZ = 0.04
BW_FILTER_ORDER = 3


def filter_with_savitzky_golay(df, window_length=SG_WINDOW_LENGTH, polyorder=SG_POLY_ORDER):
    filtered = df.copy()
    for col in df.columns:
        if col == "time":
            continue
        if len(df[col]) >= window_length:
            filtered[col] = savgol_filter(df[col], window_length, polyorder)
        # else: too few points for this window; leave the column unchanged.
    return filtered


def _design_butterworth(sampling_rate_hz):
    nyquist = 0.5 * sampling_rate_hz
    normal_cutoff = BW_CUTOFF_FREQ_HZ / nyquist
    return butter(N=BW_FILTER_ORDER, Wn=normal_cutoff, btype="low", analog=False)


def filter_with_butterworth(df, sampling_rate_hz=BW_SAMPLING_RATE_HZ):
    """Zero-phase (`filtfilt`) Butterworth low-pass.

    `sampling_rate_hz` is not derived from the data: callers must pass the
    table's actual sample spacing if it isn't the default 5 s.
    """
    b, a = _design_butterworth(sampling_rate_hz)
    filtered = df.copy()
    for col in df.columns.drop("time"):
        filtered[col] = filtfilt(b, a, df[col])
    return filtered
