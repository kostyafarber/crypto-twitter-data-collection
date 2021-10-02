import os
import datetime
from binance import Client

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

client = Client(api_key=api_key, api_secret=api_secret)

symbol = 'BTCAUD'

candles = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

print(datetime.datetime.fromtimestamp(candles[0][0]/1000))

