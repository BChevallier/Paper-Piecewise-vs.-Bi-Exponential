import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Control which treadmill_data to plot
includeUnfilteredData = False
include_bw_filtered_data = False
show_breakpoints = False  # Set to False to hide breakpoints

# File paths
sg_filtered_path = '../../treadmill_data/prepared_data/sg_filtered_4mintt.csv'
bw_filtered_path = '../../treadmill_data/prepared_data/bw_filtered_4mintt.csv'
unfiltered_path = '../../treadmill_data/prepared_data/cleaned_4mintt.csv'
gen_data_path = '../../treadmill_data/prepared_data/preparedGeneralData.csv'
breakpoints_path = '../../treadmill_data/breakpoints_by_method/tt4_breakpoints_piecewise.csv'

# Load treadmill_data
df_sg = pd.read_csv(sg_filtered_path)
df_bw = pd.read_csv(bw_filtered_path) if include_bw_filtered_data else None
df_unfiltered = pd.read_csv(unfiltered_path) if includeUnfilteredData else None
breakpoints = pd.read_csv(breakpoints_path, index_col=0) if show_breakpoints else None

# Load general treadmill_data
gen_df = pd.read_csv(gen_data_path).set_index('ID')
params = gen_df[['o2_intercept_y', 'o2_slope_y', 'speedTT4']].to_dict('index')

participant_cols = [col for col in df_sg.columns if col != 'time']
n = len(participant_cols)
cols = 5
rows = int(np.ceil(n / cols))

fig, axes = plt.subplots(rows, cols, figsize=(15, 2 * rows), sharey=True, constrained_layout=True)
axes = axes.flatten()

for idx, participant in enumerate(participant_cols):
    axes[idx].plot(df_sg['time'], df_sg[participant], label='SG-filtered', alpha=0.8)
    if include_bw_filtered_data and participant in df_bw.columns:
        axes[idx].plot(df_bw['time'], df_bw[participant], label='BW-filtered', alpha=0.7)
    if includeUnfilteredData and participant in df_unfiltered.columns:
        axes[idx].plot(df_unfiltered['time'], df_unfiltered[participant], label='Unfiltered', alpha=0.5)
    if participant in params and not pd.isna(params[participant]['speedTT4']):
        intercept = params[participant]['o2_intercept_y']
        slope = params[participant]['o2_slope_y']
        speed = params[participant]['speedTT4']
        est_o2 = intercept + slope * speed
        axes[idx].plot(df_sg['time'], [est_o2]*len(df_sg), '--', label='Estimated')
    # Plot breakpoints
    if show_breakpoints and participant in breakpoints.index:
        colors = {'sg': 'r', 'bw': 'b', 'cleaned': 'g'}
        for method, color in colors.items():
            bp = breakpoints.loc[participant, method]
            if pd.notna(bp):
                axes[idx].axvline(bp, color=color, linestyle=':', alpha=0.7, label=f'{method.upper()} BP')
    axes[idx].set_title(participant)
    axes[idx].set_xlabel('Time (s)')
    axes[idx].set_ylabel('O2 Consumption')
    axes[idx].legend(fontsize='x-small')

for ax in axes[n:]:
    ax.axis('off')

fig.suptitle('Measured vs Estimated O2 Consumption Over Time by Participant')
plt.savefig('../../figures/tt4_measured_vs_estimated.png', dpi=300)
print("Plot saved as figures/tt4ParticipantOverview.png.")
plt.show()