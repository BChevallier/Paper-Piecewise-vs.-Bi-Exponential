
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

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

# DataFrame to store parameters
param_cols = ['A0', 'A1', 'tau1', 'TD1', 'A2', 'tau2', 'TD2']
params_df = pd.DataFrame(index=participants, columns=pd.MultiIndex.from_product([['sg', 'bw', 'cleaned'], param_cols]))

def biexponential(t, A0, A1, tau1, TD1, A2, tau2, TD2):
    t = np.array(t)
    t1 = np.clip(t - TD1, 0, 300)
    t2 = np.clip(t - TD2, 0, 300)
    y1 = A1 * (1 - np.exp(-t1 / tau1))
    y2 = A2 * (1 - np.exp(-t2 / tau2))
    return A0 + y1 + y2

def fit_biexponential(x, y):
    try:
        A0_guess = y[0]
        A1_guess = y.max() - y[0]
        tau1_guess = 30
        TD1_guess = 15
        A2_guess = A1_guess * 0.2
        tau2_guess = 100
        TD2_guess = 120
        bounds = ([0, 0, 1, 0, 0, 10, 30], [5, 5, 100, 60, 5, 300, 240])
        popt, _ = curve_fit(
            biexponential, x, y,
            p0=[A0_guess, A1_guess, tau1_guess, TD1_guess, A2_guess, tau2_guess, TD2_guess],
            bounds=bounds,
            maxfev=10000
        )
        y_hat = biexponential(x, *popt)
        rmse = np.sqrt(np.mean((y - y_hat) ** 2))
        amplitude = np.max(y) - np.min(y)
        rmse_pct = (rmse / amplitude) * 100 if amplitude != 0 else np.nan
        return popt, popt[6], rmse_pct
    except Exception:
        return [np.nan]*7, np.nan, np.nan

for participant in participants:
    x = df_sg['time'].values
    # SG
    y = df_sg[participant].values
    popt, bp, rmse_pct = fit_biexponential(x, y)
    results.loc[participant, 'sg'] = bp
    rmse_pct_results.loc[participant, 'sg'] = rmse_pct
    params_df.loc[participant, ('sg',)] = popt

    # BW
    y = df_bw[participant].values
    popt, bp, rmse_pct = fit_biexponential(x, y)
    results.loc[participant, 'bw'] = bp
    rmse_pct_results.loc[participant, 'bw'] = rmse_pct
    params_df.loc[participant, ('bw',)] = popt

    # Cleaned
    y = df_cleaned[participant].values
    popt, bp, rmse_pct = fit_biexponential(x, y)
    results.loc[participant, 'cleaned'] = bp
    rmse_pct_results.loc[participant, 'cleaned'] = rmse_pct
    params_df.loc[participant, ('cleaned',)] = popt

results.to_csv('../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_breakpoints_biexponential.csv')
rmse_pct_results.to_csv('../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_breakpoints_biexponential_rmse_pct.csv')
params_df.to_csv('../../treadmill_data/breakpoints_and_modelFit_by_method/tt4_biexponential_params.csv')
print('Bi-exponential breakpoints, RMSE percentages, and parameter values saved.')