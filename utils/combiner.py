# just an interim solution to combine the datasets
import os
import pandas as pd

def combine_data(path):
    files = os.listdir(path)
    data = []
    for file in files:
        data.append(pd.read_csv(f"{path}/{file}"))
    
    pd.concat(data).to_csv(f"{path}/combined.csv", index=False)

combine_data("out/2")