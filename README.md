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
- **Cycling** (`bike_data/`, `bike_code/`) — an in-progress second arm of
  the same comparison, currently only as far as raw-to-filtered data; no
  breakpoint/model-fitting step exists for it yet, and it is not part of
  the published results.

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

bike_data/, bike_code/,
code/data_processing/bike/
                         cycling arm, work in progress (see Status above)
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
