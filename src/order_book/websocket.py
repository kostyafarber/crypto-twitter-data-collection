import os
import datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import time

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]
symbol = 'BTCUSDT'


class DataCollector(ThreadedWebsocketManager):
    def __init__(self, api_key, api_secret, symbol):

        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol

test = DataCollector(api_key, api_secret, symbol)

if __name__ == '__main__':
    print(test.api_secret)
    #print(test.timestamp)