import os
import datetime
from binance import ThreadedWebsocketManager, Client
from binance.client import BinanceAPIException
import pandas as pd
import json

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]
quote_asset = 'DOGE'
base_asset = 'AUD'

class Broker(Client):
    def __init__(self, api_key, api_secret, base_asset, quote_asset):
        super().__init__(api_key, api_secret)
        
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.order_book = pd.DataFrame()
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = quote_asset + base_asset

    def get_base_balance(self):
        balance = self.get_asset_balance(asset=base_asset)
        return balance

    def stream_order_book(self, symbol, time_delta):

        self.symbol = symbol
        self.time_delta = time_delta

        stop_time = datetime.datetime.now()
        stop_time = stop_time + datetime.timedelta(seconds=time_delta)

        twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret)

        print("Connecting to socket...")
        twm.start()

        def handle_socket_message(msg):
        
            timestamp = datetime.datetime.fromtimestamp(msg['E']/1000)
            #stop_time = timestamp + datetime.timedelta(seconds=5)
            bids = msg['b']
            asks = msg['a']

            data = dict(timestamp=timestamp, bids=bids, asks=asks)

            df = pd.json_normalize(data)
            self.order_book = pd.concat([self.order_book, df], ignore_index=True)
            print(self.order_book)

            if stop_time < timestamp:

                    print("Closing Connection...")
                    print("Saving " + symbol + ' order book data')
                    #twm.stop_socket(stream)
                    twm.stop()

            elif msg['e'] == 'error':

                # save log of error
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(msg, f, ensure_ascii=False, indent=4)
                
                # restart stream
                twm.stop(stream)
                twm.start()
                twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

        stream = twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

        twm.join()

    
broker = Broker(api_key=api_key, api_secret=api_secret, base_asset=base_asset, quote_asset=quote_asset)

if __name__ == '__main__':

    #broker.stream_order_book('BTCAUD', 10)
    #print(broker.get_base_balance())
    #print(broker.get_ticker(symbol=broker.symbol))
    #print(broker.symbol)
    #broker
    #print(broker.get_all_orders(symbol=broker.symbol))
    price = broker.get_symbol_ticker(symbol=broker.symbol)
    print(price['price'])

    