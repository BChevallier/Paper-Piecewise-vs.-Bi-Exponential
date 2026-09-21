# Treadmill prepared data

Written by the treadmill scripts from `../raw/`; regenerate rather than edit.

- **general_data.csv**
  Participant-level physiological and performance data, with selected columns,
  unit conversions and derived variables. From `raw/general_data.csv` by
  `01_prepare_general_data.py`.

- **time_trial.csv**
  VO2 per participant during the 4-min time trial, time in seconds from the
  trial start, pre- and post-trial rows removed. From `raw/time_trial.csv` by
  `02_prepare_time_trial_data.py`. The models' unfiltered ("cleaned") input.

- **time_trial_sg_filtered.csv**
  `time_trial.csv` smoothed with a Savitzky-Golay filter, by
  `03_filter_savitzky_golay.py`.

- **time_trial_bw_filtered.csv**
  `time_trial.csv` smoothed with a Butterworth low-pass filter, by
  `04_filter_butterworth.py`.
