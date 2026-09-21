"""Step 5 of the bike pipeline: plot every participant's V'O2 response.

The bike counterpart of the treadmill's `07_plot_participants.py`: a grid of
V'O2 vs. time, one subplot per participant, showing the Savitzky-Golay curve.
The `INCLUDE_*` / `SHOW_BREAKPOINTS` flags optionally overlay the
Butterworth-filtered curve, the unfiltered 5-s data, and each method's
piecewise breakpoint (from `05_fit_piecewise.py`).

There is no "estimated" reference line: the treadmill one comes from each
runner's VO2-speed regression, which has no cycling equivalent in this data.

Writes `bike/figures/<trial>_participants.png`.

Usage:
    python bike/scripts/07_plot_participants.py        # both trials
    python bike/scripts/07_plot_participants.py tt1    # one trial
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bike_common import (
    FIGURES_DIR,
    REPO_ROOT,
    RESULTS_DIR,
    bw_filtered_path,
    prepared_path,
    requested_trials,
    sg_filtered_path,
)

# Toggle optional overlays.
INCLUDE_UNFILTERED_DATA = False
INCLUDE_BW_FILTERED_DATA = False
SHOW_BREAKPOINTS = False

SUBPLOT_COLUMNS = 5
BREAKPOINT_COLORS = {"sg": "r", "bw": "b", "cleaned": "g"}


def plot_trial(trial):
    df_sg = pd.read_csv(sg_filtered_path(trial))
    df_bw = pd.read_csv(bw_filtered_path(trial)) if INCLUDE_BW_FILTERED_DATA else None
    df_unfiltered = pd.read_csv(prepared_path(trial)) if INCLUDE_UNFILTERED_DATA else None
    breakpoints = (
        pd.read_csv(RESULTS_DIR / f"{trial}_piecewise_breakpoints.csv", index_col=0)
        if SHOW_BREAKPOINTS else None
    )

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

        if INCLUDE_BW_FILTERED_DATA:
            ax.plot(df_bw["time"], df_bw[participant], label="BW-filtered", alpha=0.7)

        if INCLUDE_UNFILTERED_DATA:
            ax.plot(df_unfiltered["time"], df_unfiltered[participant], label="Unfiltered", alpha=0.5)

        if SHOW_BREAKPOINTS and participant in breakpoints.index:
            for method, color in BREAKPOINT_COLORS.items():
                bp = breakpoints.loc[participant, method]
                if pd.notna(bp):
                    ax.axvline(bp, color=color, linestyle=":", alpha=0.7, label=f"{method.upper()} BP")

        ax.set_title(participant)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("V'O2 (L/min)")
        ax.legend(fontsize="x-small")

    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle(f"Cycling time trial {trial}: V'O2 over time by participant")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / f"{trial}_participants.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"{trial}: plot saved to {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    for trial in requested_trials(sys.argv):
        plot_trial(trial)
