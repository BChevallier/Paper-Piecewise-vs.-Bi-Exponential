# Cycling data

Two 4-min cycling time trials per participant, `tt1` and `tt2`, recorded
breath-by-breath (exported at 1 s) on a Cortex MetaLyzer 3B spirometer.

- **raw/cpet_exports/** — `<trial>_cpet_pNN.xml`, the spirometry software's
  exports (Excel 2003 SpreadsheetML despite the extension). Facility contact
  fields are blanked by `00_anonymize_cpet_exports.py`; otherwise as exported.
- **raw/delay_anmedu.xlsx** — per-participant offset (s) by which the
  spirometer clock lags real time, per test. The trial starts 180 s into the
  session in real time, i.e. at `180 - delay` on the spirometer clock.
- **converted/<trial>/** — `<trial>_pNN.csv`, the measurement table of each
  export as CSV, one row per second (`01_xml_to_csv.py`).
- **master_table.csv** — one row per participant: demographics and summary
  performance/physiology for each test (power, heart rate, VO2peak, lactate,
  RPE, efficiency, ...). Not used by the scripts.
- **prepared/** — the model inputs, one wide table per trial: `time` (0-240 s
  in 5-s steps) plus one V'O2 column per participant.
  - `<trial>_time_trial.csv` — 5-s mean V'O2 (`02_prepare_time_trial_data.py`)
  - `<trial>_time_trial_sg_filtered.csv` — Savitzky-Golay smoothed (`03`)
  - `<trial>_time_trial_bw_filtered.csv` — Butterworth smoothed (`04`)
