import os
import datetime
from binance import ThreadedWebsocketManager, Client
import pandas as pd
import json

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]
quote_asset = 'BTC'
base_asset = 'BNB'

class Broker(Client):
    def __init__(self, api_key, api_secret, base_asset, quote_asset):
        super().__init__(api_key, api_secret)
        
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.order_book = pd.DataFrame()
        self.api_key = api_key
        self.api_secret = api_secret

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
            order_book = pd.concat([self.order_book, df], ignore_index=True)
            print(order_book)

            if timestamp > stop_time:
                    
                print("Closing Connection...")
                print("Saving " + symbol + ' order book data')
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

    broker.stream_order_book('BTCAUD', 5)
    #print(broker.get_base_balance())
