# Treadmill model results

One row per participant; one column per signal variant: `sg` (Savitzky-Golay),
`bw` (Butterworth), `cleaned` (unfiltered). Written by `treadmill/scripts/05_fit_piecewise.py` and `06_fit_biexponential.py`.

- **piecewise_breakpoints.csv**
  Breakpoint (s) of the two-segment piecewise-linear fit.

- **piecewise_rmse_pct.csv**
  RMSE of the piecewise fit, as % of the signal's amplitude.

- **biexponential_breakpoints.csv**
  `TD2`, the slow component's time delay (s), treated as the bi-exponential
  model's breakpoint. Not the same quantity as the piecewise breakpoint; see
  the top-level README.

- **biexponential_rmse_pct.csv**
  RMSE of the bi-exponential fit, as % of the signal's amplitude.

- **biexponential_params.csv**
  All seven fitted parameters (`A0, A1, tau1, TD1, A2, tau2, TD2`) per
  signal variant; two header rows (variant, parameter).
