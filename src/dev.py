import os
import datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

symbol = 'BNBBTC'

def main():

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    twm.start()

    def handle_socket_message(msg):

        date = datetime.datetime.fromtimestamp(msg['k']['t']/1000)
        
        print(f"{date} {msg['k']['o']}")  

    
    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    twm.join()

if __name__ == "__main__":
   main()