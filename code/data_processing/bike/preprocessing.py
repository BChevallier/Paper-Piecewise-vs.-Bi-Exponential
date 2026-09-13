import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PATH = "../../../bike_data/raw_data/delay_anmedu.xlsx"

df = pd.read_excel(PATH)

print(df.columns.to_list())
df=df[["delay_cpet_tt0","delay_cpet_tt1","delay_cpet_tt2"]]
df["id"]=[i for i in range(1,len(df)+1)]
df.set_index("id",inplace=True)
print(df)

def clean(i):
    PATH_SPIRO = f"../../../bike_data/prepared_data/tt1/tt1_p{i:02d}.csv"
    df_i = pd.read_csv(PATH_SPIRO)
    print(df_i)

clean(1)

