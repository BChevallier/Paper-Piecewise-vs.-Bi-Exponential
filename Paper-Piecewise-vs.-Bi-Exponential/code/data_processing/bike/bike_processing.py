import pandas as pd
from matplotlib import pyplot as plt

PATH= "../../../bike_data/raw_data/tt1/tt1_p02.csv"

df=pd.read_csv(PATH)

df["t"]=pd.to_timedelta(df["t"])
df.set_index("t", inplace=True)

delay=50

delay=pd.Timedelta(f"00:00:{str(delay).zfill(2)}")
df=df[df.index>=delay]

df.plot(y=["V'O2"])
plt.show()
