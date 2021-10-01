import os
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

api_key = os.environ["BINANCE_API"]
api_secret = os.environ["BINANCE_API_SECRET"]

client = Client(api_key, api_secret)

prices = client.get_all_tickers()

twm = ThreadedWebsocketManager()
twm.start()

def handle_socket_message(msg):
    print(f"message type: {msg['e']}")
    print(msg)

twm.start_kline_socket(callback=handle_socket_message, symbol='BNBBTC')

