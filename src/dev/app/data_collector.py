from deribit import DeribitClient
from datetime import datetime
import pandas as pd
import os
import json


client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]

exchange_version = 'wss://www.deribit.com/ws/api/v2/'

class DataCollector(DeribitClient):
    def __init__(self, client_id, client_secret, testnet=False) -> None:
        """Generates order book data. Can collect and save to csv.

        Args:
            client_id (str): Public API Key
            client_secret (str): Private API Key
            testnet (bool, optional): Whether to use tesnet exchange. Defaults to False.
        """
        super().__init__(client_id, client_secret, testnet=testnet)

    def add_args(self):
        self.parser.add_argument('--csv', type=bool)
        self.parser_add_argument('--aws', type=bool)
        return super().add_args()

    def _process_callback(self, response: json):
        """Override this method to process the callback message

        Args:
            response (json): Contains the response message from the websocket.
        """

        # processes LOB data
        if 'params' in response.keys() and response['method'] == 'subscription':
            if response['params']['channel'] == 'book.BTC-PERPETUAL.none.10.100ms':

                timestamp = datetime.fromtimestamp(response['params']['data']['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                bids = response['params']['data']['bids']
                asks = response['params']['data']['asks']

                total_bids = 0
                total_asks = 0
                for bid, ask in zip(bids, asks):
                    total_bids += bid[1]
                    total_asks += ask[1]
                
                mid_price = (bids[0][0] + asks[0][0])/2
                net_ofi = (total_bids - total_asks)/(total_bids + total_asks)
                data = dict(timestamp=[timestamp], mid_price=[mid_price], net_ofi=[net_ofi])

                df = pd.DataFrame(data)
                df.set_index('timestamp')

                self.orderbook = pd.concat([self.orderbook, df], ignore_index=True)
                
                print(self.orderbook)
                
                instrument = response['params']['data']['instrument_name']

                if self.args.csv:
                
                    # header on only the first entry
                    if len(self.orderbook.index) == 1:
                        self.orderbook.tail(1).to_csv(f'{instrument}-{self.time}.csv', mode='a')

                    else:
                        self.orderbook.tail(1).to_csv(f'{instrument}-{self.time}.csv', mode='a', header=False)    

            if response['params']['channel'] == 'ticker.BTC-PERPETUAL.raw':
                
                stats = response['params']['data']['stats']
                timestamp = datetime.fromtimestamp(response['params']['data']['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S')
                volume = stats['volume_usd']

                print(f"{timestamp} Volume: {volume}")

                
    
    def _on_open_message(self):

        # To subscribe to this channel:
        msg = \
            {"jsonrpc": "2.0",
            "method": "public/subscribe",
            "id": 42,
            "params": {
                "channels": ["ticker.BTC-PERPETUAL.raw", 'book.BTC-PERPETUAL.none.10.100ms']}
            }
        
        self.ws.send(json.dumps(msg))

if __name__ == '__main__':

    test = DataCollector(client_id, client_secret)
    test.start()