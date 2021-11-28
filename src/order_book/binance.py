import os
import datetime
from binance import ThreadedWebsocketManager
import pandas as pd

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

stop_time = datetime.datetime(2021, 11, 4, 21, 53)

symbol = 'BTCUSDT'

order_book = pd.DataFrame()

def main():
    
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    print("Connecting to socket...")
    twm.start()

    def handle_socket_message(msg):

        timestamp = datetime.datetime.fromtimestamp(msg['E']/1000)
        bids = msg['b']
        asks = msg['a']

        data = dict(timestamp=timestamp, bids=bids, asks=asks)
        
        global order_book

        df = pd.json_normalize(data)
        order_book = pd.concat([order_book, df], ignore_index=True)
        print(order_book)
        
        global stop_time

        if order_book.timestamp.iloc[-1] > stop_time:
            
            print("Closing Connection...")
            print("Saving " + symbol + 'order book data')
            order_book.to_pickle('test.pkl')

            twm.stop()

    twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)
    
    twm.join()

if __name__ == "__main__":
    main()

