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

- **Treadmill running** (`treadmill_data/`, `code/`) — the complete,
  published pipeline: raw data all the way through to breakpoint/model-fit
  results and figures. Documented below.
- **Cycling** (`bike_data/`, `bike_code/`) — a second arm of the same
  comparison: two 4-min cycling time trials (`tt1`, `tt2`) run through the
  same smoothing and the same two models as the treadmill data. Documented
  below; not yet part of the published results.

## Repository layout

```
treadmill_data/
  raw_data/            as recorded; generalData.csv (one row per
                        participant) and timeTrial.csv (VO2 time series
                        during the 4-min trial). See 0-raw_data-overview.md
                        for column definitions.
  prepared_data/        outputs of code/data_processing/run/*.py
  breakpoints_and_modelFit_by_method/
                         outputs of code/vo2_modeling/*.py — the actual
                         results (breakpoints, RMSE%, fitted parameters)

code/
  data_processing/run/  steps 1-4: clean, trim, and smooth the raw data
  vo2_modeling/          steps 5-6: fit both models, per participant and
                         per smoothing method
  data_visualization/    step 7: plot every participant's response

figures/                 output of the visualization step

bike_data/
  raw_data/              CPET exports (ergo_data/), per-second CSVs
                         (tt1/, tt2/), clock offsets (delay_anmedu.xlsx)
  prepared_data/         outputs of bike_code/02-04
  breakpoints_and_modelFit_by_method/
                         outputs of bike_code/05-06
bike_code/               cycling pipeline, steps 0-7 (see below)
code/data_processing/bike/
                         early exploratory scripts, superseded by bike_code/
```

## Reproducing the treadmill pipeline

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the seven numbered scripts in order (each can be run from any
working directory — paths are resolved relative to the script's own
location, not the shell's current directory):

| # | Script | Reads | Writes |
|---|--------|-------|--------|
| 1 | `code/data_processing/run/01_prepare_general_data.py` | `treadmill_data/raw_data/generalData.csv` | `treadmill_data/prepared_data/preparedGeneralData.csv` |
| 2 | `code/data_processing/run/02_prepare_time_trial_data.py` | `treadmill_data/raw_data/timeTrial.csv` | `treadmill_data/prepared_data/preparedTimeTrial.csv` |
| 3 | `code/data_processing/run/03_filter_savitzky_golay.py` | `preparedTimeTrial.csv` | `treadmill_data/prepared_data/sg_filtered_4mintt.csv` |
| 4 | `code/data_processing/run/04_filter_butterworth.py` | `preparedTimeTrial.csv` | `treadmill_data/prepared_data/bw_filtered_4mintt.csv` |
| 5 | `code/vo2_modeling/05_fit_piecewise.py` | all three prepared/filtered time series | `tt4_breakpoints_piecewise.csv`, `..._rmse_pct.csv` |
| 6 | `code/vo2_modeling/06_fit_biexponential.py` | all three prepared/filtered time series | `tt4_breakpoints_biexponential.csv`, `..._rmse_pct.csv`, `tt4_biexponential_params.csv` |
| 7 | `code/data_visualization/07_plot_participants.py` | filtered data + `preparedGeneralData.csv` (+ optionally step 5's breakpoints) | `figures/tt4_measured_vs_estimated.png` |

Steps 3 and 4 are independent of each other (both only need step 2's
output) and can run in either order. Steps 5 and 6 are likewise
independent, each comparing its own model across the same three signal
variants: `sg` (Savitzky-Golay filtered), `bw` (Butterworth filtered), and
`cleaned` (no smoothing — the direct output of step 2).

**Note on reproducibility:** steps 1-4 are deterministic and will
reproduce the committed output files exactly. Steps 5-6 involve nonlinear
optimization (`pwlf`'s piecewise fit, `scipy.optimize.curve_fit`'s
bi-exponential fit); re-running them can shift fitted values by a small
amount (observed: differences at roughly the 4th-6th significant digit)
depending on installed `numpy`/`scipy`/`pwlf` versions and BLAS backend.
The committed result files in `treadmill_data/breakpoints_and_modelFit_by_method/`
are the ones actually used for the published analysis — treat re-run
output as a correctness check on the *pipeline*, not a byte-identical
replacement for those files.

## Reproducing the cycling pipeline

Same environment as above. Each script takes an optional trial argument
(`tt1` or `tt2`) and runs both when given none.

| # | Script | Reads | Writes |
|---|--------|-------|--------|
| 0 | `bike_code/00_anonymize_ergo_data.py` | `bike_data/raw_data/ergo_data/*.xml` | the same files, facility contact fields blanked (only needed after importing new exports) |
| 1 | `bike_code/01_xml_to_csv.py` | `ergo_data/<trial>_cpet_pNN.xml` | `bike_data/raw_data/<trial>/<trial>_pNN.csv` |
| 2 | `bike_code/02_prepare_time_trial_data.py` | per-second CSVs + `delay_anmedu.xlsx` | `bike_data/prepared_data/<trial>_prepared_time_trial.csv` |
| 3 | `bike_code/03_filter_savitzky_golay.py` | step 2's table | `<trial>_sg_filtered.csv` |
| 4 | `bike_code/04_filter_butterworth.py` | step 2's table | `<trial>_bw_filtered.csv` |
| 5 | `bike_code/05_fit_piecewise.py` | all three signal variants | `<trial>_breakpoints_piecewise.csv`, `..._rmse_pct.csv` |
| 6 | `bike_code/06_fit_biexponential.py` | all three signal variants | `<trial>_breakpoints_biexponential.csv`, `..._rmse_pct.csv`, `<trial>_biexponential_params.csv` |
| 7 | `bike_code/07_plot_participants.py` | filtered data (+ optionally step 5's breakpoints) | `figures/bike_<trial>_participants.png` |

Steps 3-6 call the same functions as treadmill steps 3-6
(`code/data_processing/run/smoothing.py`, `code/vo2_modeling/piecewise_model.py`,
`biexponential_model.py`, `metrics.py`), with the same settings, so the two
modalities differ only in their data.

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

`bike_code/filter_and_trim_data.py` is a supplementary per-second export of
each trial (all channels, V'O2 low-pass filtered) in
`bike_data/prepared_data/<trial>/`, kept for inspection; the models do not
use it.

## Interpreting the two models' "breakpoints"

The piecewise model's breakpoint is the single fitted junction between its
two linear segments. The bi-exponential model's "breakpoint" (as reported
in `tt4_breakpoints_biexponential.csv`) is `TD2`: the time delay of its
second (slow) exponential component. These are related but not the same
quantity, and in practice land at quite different points in the response
(the piecewise breakpoint tends to fall much earlier than TD2) — see
`code/vo2_modeling/biexponential_model.py`'s module docstring for the full
model definition, and don't assume the two numbers are directly comparable
without accounting for what each one actually measures.

## License

See [LICENSE](LICENSE).
