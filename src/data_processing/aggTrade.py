import os
import pandas as pd
from utils import *
import glob
import matplotlib.pyplot as plt

def preprocess_chunk(filepath):
    
    chunk = pd.read_csv(filepath, 
                    names=labels_aggTrades, 
                    date_parser=parse_dates, 
                    parse_dates=["Timestamp"], 
                    index_col='Timestamp',
                    chunksize=100000)
    
    return chunk

data_path = '../data/data/spot/monthly/aggTrades/ETHBTC/*'

files = glob.glob(data_path)

data = pd.DataFrame()

for f in files[0]:

    chunks = [chunk for chunk in preprocess_chunk(f)]

    merged = pd.concat(chunks)

    data = pd.concat([data, merged])

data.to_pickle("etcbtc")

if __name__ == '__main__':
    pass