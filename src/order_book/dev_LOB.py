import os
import datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import time

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

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
        #print(date)
        #print(f"Date: {date} Bids: {msg['b']} Asks: {msg['a']}")  
        global order_book

        df = pd.json_normalize(data)
        order_book = pd.concat([order_book, df], ignore_index=True)
        #test.append(bids)
        print(order_book)

    stream = twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)
    
    #twm.join()

    time.sleep(10)
    print("Closing Connection...")
    twm.stop_socket(stream)

    twm.stop()

    print("Saving " + symbol + 'order book data')
    order_book.to_pickle('test.pkl')

if __name__ == "__main__":
    main()

