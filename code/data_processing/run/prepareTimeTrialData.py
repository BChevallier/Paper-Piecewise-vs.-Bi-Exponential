import pandas as pd

#converts minute string to seconds integer
def min_to_seconds(list_of_timestamps: [str]) -> int:
    m, s = map(int, list_of_timestamps.split(':'))
    return m*60+s

dataToPrepare = "../../treadmill_data/raw_data/timeTrial.csv"
df = pd.read_csv(dataToPrepare)


## Prepare 4min treadmill_data for reading
#drop unnecessary rows
df.drop(df.index[107:121], inplace=True)
df.drop(df.index[0:58], inplace=True)

#drop unnecessary columns
df.drop(columns=df.columns[-5:], inplace=True)

#set time in seconds as index
df['time'] = df['time'].apply(min_to_seconds) - 300
df.set_index('time', inplace=True)

df.to_csv("../../treadmill_data/prepared_data/preparedTimeTrial.csv")