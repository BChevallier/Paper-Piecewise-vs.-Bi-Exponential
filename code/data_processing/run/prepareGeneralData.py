import pandas as pd

totalData="../../treadmill_data/raw_data/generalData.csv"
colsToKeep = ["ID", "o2_intercept_y", "o2_slope_y","tt4_d","vo2_max_abs","body_mass","D","cs","t_100", "cmj","mss"]

#read treadmill_data
df = pd.read_csv(totalData)[colsToKeep]

#converts mililiter to liter
def mLtoL(x):
    return x/1_000

#converts 1/(km/h) to 1/(m/s)
def perkmHtoperms(x):
    return x*3.6

#converts the distance run in 4 min to average speed
def distTT4toSpeed(x):
    return x/240

df["o2_intercept_y"]=df["o2_intercept_y"].apply(mLtoL)
df["o2_slope_y"]=df["o2_slope_y"].apply(mLtoL)
df["o2_slope_y"]=df["o2_slope_y"].apply(perkmHtoperms)
df["speedTT4"]=df["tt4_d"].apply(distTT4toSpeed)
df.drop(columns=["tt4_d"], inplace=True)

#saves the new csv
df.to_csv("../../treadmill_data/prepared_data/preparedGeneralData.csv")