# Piecewise vs. Bi-Exponential

Code and data behind a comparison of two ways to model the VO2 (oxygen
uptake) response during a short, self-paced exercise time trial:

1. **Piecewise-linear** — a two-segment linear fit with one breakpoint
   (via [`pwlf`](https://github.com/cjekel/piecewise_linear_fit_py)).
2. **Bi-exponential** — a seven-parameter model with two independently
   time-delayed exponential components (fast/primary and slow), fit with
   `scipy.optimize.curve_fit`.

The question this asks: where does the VO2 response show a "breakpoint" or
inflection, and does the answer depend on which of the two modeling
methods is used, or on which signal-smoothing method is applied
beforehand? Fit quality for both methods is judged by RMSE, expressed as a
percentage of each participant's signal amplitude.

This repository is not a general-purpose analysis tool — it is a
record of the exact steps used to go from the raw, recorded data to the
figures/tables used in the write-up, kept in a form other researchers can
read and re-run. Every step is a separate, numbered, documented script;
none of the raw data is ever edited by hand, only read and transformed by
these scripts into new files.

## Status

- **Treadmill running** (`treadmill/`) — the complete, published pipeline:
  raw data all the way through to breakpoint/model-fit results and figures.
- **Cycling** (`bike/`) — a second arm of the same comparison: two 4-min
  cycling time trials (`tt1`, `tt2`) run through the same smoothing and the
  same two models as the treadmill data. Not yet part of the published
  results.

## Repository layout

Each arm is a self-contained folder with the same structure; the code both
arms share lives in `shared/`.

```
shared/                   smoothing and model code used by both arms
  smoothing.py              Savitzky-Golay and Butterworth filters
  piecewise_model.py        two-segment piecewise-linear fit (pwlf)
  biexponential_model.py    bi-exponential model and fit (curve_fit)
  metrics.py                RMSE as % of signal amplitude

treadmill/
  scripts/                steps 01-07, run in order
  data/raw/               as recorded (see its README for columns)
  data/prepared/          outputs of steps 01-04
  results/                outputs of steps 05-06: breakpoints, RMSE%, parameters
  figures/                output of step 07

bike/
  scripts/                steps 00-07, run in order
  data/raw/               spirometer exports and clock offsets
  data/converted/         exports as per-second CSVs (step 01)
  data/prepared/          outputs of steps 02-04
  data/master_table.csv   per-participant summary table
  results/                outputs of steps 05-06
  figures/                output of step 07
```

Every data and results folder has a README describing its files.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Every script can be run from any working directory: paths are resolved
relative to the script's own location. Each arm's `*_common.py` holds its
paths and makes `shared/` importable.

## Reproducing the treadmill pipeline

Run the seven numbered scripts in `treadmill/scripts/` in order:

| # | Script | Reads | Writes |
|---|--------|-------|--------|
| 1 | `01_prepare_general_data.py` | `data/raw/general_data.csv` | `data/prepared/general_data.csv` |
| 2 | `02_prepare_time_trial_data.py` | `data/raw/time_trial.csv` | `data/prepared/time_trial.csv` |
| 3 | `03_filter_savitzky_golay.py` | `time_trial.csv` | `data/prepared/time_trial_sg_filtered.csv` |
| 4 | `04_filter_butterworth.py` | `time_trial.csv` | `data/prepared/time_trial_bw_filtered.csv` |
| 5 | `05_fit_piecewise.py` | all three time series | `results/piecewise_breakpoints.csv`, `results/piecewise_rmse_pct.csv` |
| 6 | `06_fit_biexponential.py` | all three time series | `results/biexponential_breakpoints.csv`, `results/biexponential_rmse_pct.csv`, `results/biexponential_params.csv` |
| 7 | `07_plot_participants.py` | filtered data + `general_data.csv` (+ optionally step 5's breakpoints) | `figures/measured_vs_estimated.png` |

Paths are relative to `treadmill/`. Steps 3 and 4 are independent of each
other (both only need step 2's output) and can run in either order. Steps 5
and 6 are likewise independent, each comparing its own model across the
same three signal variants: `sg` (Savitzky-Golay filtered), `bw`
(Butterworth filtered), and `cleaned` (no smoothing — the direct output of
step 2).

**Note on reproducibility:** steps 1-4 are deterministic and will
reproduce the committed output files exactly. Steps 5-6 involve nonlinear
optimization (`pwlf`'s piecewise fit, `scipy.optimize.curve_fit`'s
bi-exponential fit); re-running them can shift fitted values by a small
amount (observed: differences at roughly the 4th-6th significant digit)
depending on installed `numpy`/`scipy`/`pwlf` versions and BLAS backend.
The committed result files in `treadmill/results/` are the ones actually
used for the published analysis — treat re-run output as a correctness
check on the *pipeline*, not a byte-identical replacement for those files.

## Reproducing the cycling pipeline

Run the numbered scripts in `bike/scripts/` in order. Each takes an optional
trial argument (`tt1` or `tt2`) and runs both when given none.

| # | Script | Reads | Writes |
|---|--------|-------|--------|
| 0 | `00_anonymize_cpet_exports.py` | `data/raw/cpet_exports/*.xml` | the same files, facility contact fields blanked (only needed after importing new exports) |
| 1 | `01_xml_to_csv.py` | `data/raw/cpet_exports/<trial>_cpet_pNN.xml` | `data/converted/<trial>/<trial>_pNN.csv` |
| 2 | `02_prepare_time_trial_data.py` | per-second CSVs + `data/raw/delay_anmedu.xlsx` | `data/prepared/<trial>_time_trial.csv` |
| 3 | `03_filter_savitzky_golay.py` | step 2's table | `data/prepared/<trial>_time_trial_sg_filtered.csv` |
| 4 | `04_filter_butterworth.py` | step 2's table | `data/prepared/<trial>_time_trial_bw_filtered.csv` |
| 5 | `05_fit_piecewise.py` | all three time series | `results/<trial>_piecewise_breakpoints.csv`, `results/<trial>_piecewise_rmse_pct.csv` |
| 6 | `06_fit_biexponential.py` | all three time series | `results/<trial>_biexponential_breakpoints.csv`, `results/<trial>_biexponential_rmse_pct.csv`, `results/<trial>_biexponential_params.csv` |
| 7 | `07_plot_participants.py` | filtered data (+ optionally step 5's breakpoints) | `figures/<trial>_participants.png` |

Paths are relative to `bike/`. Steps 3-6 call the same `shared/` functions
as treadmill steps 3-6, with the same settings, so the two arms differ only
in their data.

Two things differ from the treadmill data and are handled in step 2:

- **Clock offset.** The spirometer's clock lags real time by a
  per-participant amount recorded in `delay_anmedu.xlsx`. The trial starts
  180 s into the session in real time, i.e. at `180 - delay` on the
  spirometer clock.
- **Sampling.** The cycling data is per-second; the treadmill data is in
  5-second samples, and the smoothing settings are defined on that grid.
  Step 2 averages V'O2 into 5-second bins from 0 to 240 s, each labelled by
  its end, so t = 0 holds the last 5 s before the start (the pre-trial
  baseline) as on the treadmill.

## Interpreting the two models' "breakpoints"

The piecewise model's breakpoint is the single fitted junction between its
two linear segments. The bi-exponential model's "breakpoint" (as reported
in `biexponential_breakpoints.csv`) is `TD2`: the time delay of its
second (slow) exponential component. These are related but not the same
quantity, and in practice land at quite different points in the response
(the piecewise breakpoint tends to fall much earlier than TD2) — see
`shared/biexponential_model.py`'s module docstring for the full
model definition, and don't assume the two numbers are directly comparable
without accounting for what each one actually measures.

## License

See [LICENSE](LICENSE).
