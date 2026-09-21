"""Step 5 of the treadmill pipeline: plot every participant's VO2 response.

Draws a grid (one subplot per participant) of VO2 vs. time, and saves it to
`treadmill/figures/measured_vs_estimated.png`. By default it shows only the
Savitzky-Golay-filtered curve plus a horizontal dashed reference line: the
VO2 predicted for that participant's actual average time-trial speed from
their own independently-measured VO2-speed regression
(`general_data.csv`'s `o2_intercept_y + o2_slope_y * speedTT4`) — a
sanity check for whether the time trial reached the "expected" steady
state.

The `INCLUDE_*` / `SHOW_BREAKPOINTS` flags below optionally overlay the
Butterworth-filtered curve, the unfiltered curve, and each method's fitted
breakpoint (from `05_fit_piecewise.py`) as vertical dashed lines.

Run from anywhere, e.g. `python treadmill/scripts/07_plot_participants.py`
from the repo root.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from treadmill_common import (
    FIGURES_DIR,
    GENERAL_DATA,
    RESULTS_DIR,
    TIME_TRIAL,
    TIME_TRIAL_BW,
    TIME_TRIAL_SG,
)

# Toggle optional overlays.
INCLUDE_UNFILTERED_DATA = False
INCLUDE_BW_FILTERED_DATA = False
SHOW_BREAKPOINTS = False

SG_FILTERED_PATH = TIME_TRIAL_SG
BW_FILTERED_PATH = TIME_TRIAL_BW
UNFILTERED_PATH = TIME_TRIAL
GENERAL_DATA_PATH = GENERAL_DATA
BREAKPOINTS_PATH = RESULTS_DIR / "piecewise_breakpoints.csv"

OUTPUT_PATH = FIGURES_DIR / "measured_vs_estimated.png"

SUBPLOT_COLUMNS = 5
BREAKPOINT_COLORS = {"sg": "r", "bw": "b", "cleaned": "g"}


def main():
    df_sg = pd.read_csv(SG_FILTERED_PATH)
    df_bw = pd.read_csv(BW_FILTERED_PATH) if INCLUDE_BW_FILTERED_DATA else None
    df_unfiltered = pd.read_csv(UNFILTERED_PATH) if INCLUDE_UNFILTERED_DATA else None
    breakpoints = (
        pd.read_csv(BREAKPOINTS_PATH, index_col=0) if SHOW_BREAKPOINTS else None
    )

    gen_df = pd.read_csv(GENERAL_DATA_PATH).set_index("ID")
    estimated_params = gen_df[["o2_intercept_y", "o2_slope_y", "speedTT4"]].to_dict("index")

    participant_cols = [col for col in df_sg.columns if col != "time"]
    n = len(participant_cols)
    rows = int(np.ceil(n / SUBPLOT_COLUMNS))

    fig, axes = plt.subplots(
        rows, SUBPLOT_COLUMNS, figsize=(15, 2 * rows), sharey=True, constrained_layout=True
    )
    axes = axes.flatten()

    for idx, participant in enumerate(participant_cols):
        ax = axes[idx]
        ax.plot(df_sg["time"], df_sg[participant], label="SG-filtered", alpha=0.8)

        if INCLUDE_BW_FILTERED_DATA and participant in df_bw.columns:
            ax.plot(df_bw["time"], df_bw[participant], label="BW-filtered", alpha=0.7)

        if INCLUDE_UNFILTERED_DATA and participant in df_unfiltered.columns:
            ax.plot(df_unfiltered["time"], df_unfiltered[participant], label="Unfiltered", alpha=0.5)

        if participant in estimated_params and not pd.isna(estimated_params[participant]["speedTT4"]):
            p = estimated_params[participant]
            estimated_vo2 = p["o2_intercept_y"] + p["o2_slope_y"] * p["speedTT4"]
            ax.plot(df_sg["time"], [estimated_vo2] * len(df_sg), "--", label="Estimated")

        if SHOW_BREAKPOINTS and participant in breakpoints.index:
            for method, color in BREAKPOINT_COLORS.items():
                bp = breakpoints.loc[participant, method]
                if pd.notna(bp):
                    ax.axvline(bp, color=color, linestyle=":", alpha=0.7, label=f"{method.upper()} BP")

        ax.set_title(participant)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("O2 Consumption")
        ax.legend(fontsize="x-small")

    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle("Measured vs Estimated O2 Consumption Over Time by Participant")
    plt.savefig(OUTPUT_PATH, dpi=300)
    print(f"Plot saved to {OUTPUT_PATH}")
    plt.show()


if __name__ == "__main__":
    main()
