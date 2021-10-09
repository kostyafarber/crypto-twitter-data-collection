import os
import datetime
import pandas as pd
from binance import Client

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

client = Client(api_key=api_key, api_secret=api_secret)

symbol = 'BTCAUD'

candles = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

labels_klines = ["Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset", "Number of Trades", "Taker buy base", "Taker buy Quote", "Ignore"]


data = pd.DataFrame(candles, columns=labels)

