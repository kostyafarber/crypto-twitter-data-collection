import os
import datetime
import pandas as pd
from binance import Client
import sys

sys.path.append('../src/utils.py')

from utils import labels_aggTrades, parse_dates

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]
binance_inception = int(datetime.datetime(2017, 1, 1).timestamp())
timestamp_now = int(datetime.datetime.now().timestamp())

client = Client(api_key=api_key, api_secret=api_secret)

#trades = client.get_aggregate_trades(symbol='BTCAUD', startTime=binance_inception, endTime=timestamp_now)

# Historical cryptocurrency prices from Binance
def get_data_klines(symbol):
    
    """
    Create dataframe of OHLCV cryptocurrecy from binance api 
    """

    labels = ["Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset", "Number of Trades", "Taker buy base", "Taker buy Quote", "Ignore"]

    candles = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

    data_frame = pd.DataFrame(candles, columns=labels)
    data_frame.index = pd.to_datetime(data_frame['Time'], unit='ms')
    data_frame.drop("Time", inplace=True, axis=1)

    # data ingests as string
    for column in data_frame.columns:
        if column != 'Number of Trades':
            data_frame[column] = data_frame[column].astype(float)
        else:
            data_frame[column] = data_frame[column].astype(int)

    return data_frame

# CUSUM Filter
def getTEvents(gRaw, h):
    tEvents, sPos, sNeg = [], 0, 0
    diff = gRaw.diff()

    for i in diff.index[1:]:
        sPos, sNeg = max(0, sPos + diff.loc[i]), min(0, sNeg + diff.loc[i])
        if sNeg < -h:
            sNeg = 0; tEvents.append(i)

        elif sPos > h:
            sPos=0; tEvents.append(i)

    return pd.DatetimeIndex(tEvents) 

def preprocess_chunk(filepath):
    
    chunk = pd.read_csv(filepath, 
                    names=labels_aggTrades, 
                    date_parser=parse_dates, 
                    parse_dates=["Timestamp"], 
                    index_col='Timestamp',
                    chunksize=100000)
    
    return pd.concat([chunks for chunks in chunk])

if __name__ == '__main__':
    print(datetime.datetime.fromtimestamp(trades[0]['T']/1000))
    print(binance_inception)
