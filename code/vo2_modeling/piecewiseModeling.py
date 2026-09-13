import pandas as pd
import pwlf
import numpy as np

# File paths
sg_path = '../../treadmill_data/prepared_data/sg_filtered_4mintt.csv'
bw_path = '../../treadmill_data/prepared_data/bw_filtered_4mintt.csv'
cleaned_path = '../../treadmill_data/prepared_data/preparedTimeTrial.csv'

# Load treadmill_data
df_sg = pd.read_csv(sg_path)
df_bw = pd.read_csv(bw_path)
df_cleaned = pd.read_csv(cleaned_path)

participants = [col for col in df_sg.columns if col != 'time']

results = pd.DataFrame(index=participants, columns=['sg', 'bw', 'cleaned'])
rmse_pct_results = pd.DataFrame(index=participants, columns=['sg', 'bw', 'cleaned'])

def find_breakpoint_and_rmse_pct(x, y):
    try:
        my_pwlf = pwlf.PiecewiseLinFit(x, y)
        res = my_pwlf.fit(2)
        if len(res) == 3:
            breakpoint = res[1]
            y_hat = my_pwlf.predict(x)
            rmse = np.sqrt(np.mean((y - y_hat) ** 2))
            amplitude = np.max(y) - np.min(y)
            if amplitude == 0:
                rmse_pct = np.nan
            else:
                rmse_pct = (rmse / amplitude) * 100
            return breakpoint, rmse_pct
        else:
            return np.nan, np.nan
    except Exception:
        return np.nan, np.nan

for participant in participants:
    x = df_sg['time'].values
    # SG
    y = df_sg[participant].values
    bp, rmse_pct = find_breakpoint_and_rmse_pct(x, y)
    results.loc[participant, 'sg'] = bp
    rmse_pct_results.loc[participant, 'sg'] = rmse_pct
    # BW
    y = df_bw[participant].values
    bp, rmse_pct = find_breakpoint_and_rmse_pct(x, y)
    results.loc[participant, 'bw'] = bp
    rmse_pct_results.loc[participant, 'bw'] = rmse_pct
    # Cleaned
    y = df_cleaned[participant].values
    bp, rmse_pct = find_breakpoint_and_rmse_pct(x, y)
    results.loc[participant, 'cleaned'] = bp
    rmse_pct_results.loc[participant, 'cleaned'] = rmse_pct

results.to_csv('../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_breakpoints_piecewise.csv')
rmse_pct_results.to_csv('../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_breakpoints_piecewise_rmse_pct.csv')
print('Breakpoints and RMSE percentages saved to ../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_breakpoints_piecewise.csv and tt4_breakpoints_piecewise_rmse_pct.csv')