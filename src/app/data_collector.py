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
        """Generates crpyto data. Can collect and save to csv.

        Args:
            client_id (str): Public API Key
            client_secret (str): Private API Key
            testnet (bool, optional): Whether to use tesnet exchange. Defaults to False.
        """
        
        super().__init__(client_id, client_secret, testnet=testnet)
        self._data = dict(orderbook=pd.DataFrame(), ticker=pd.DataFrame())

    def write_csv(self, data, data_type, instrument):
       
        # header on only the first entry
        if len(data.index) == 1:
            data.tail(1).to_csv(f'{data_type}-{instrument}-{self.time}.csv', mode='a')
        else:
            data.tail(1).to_csv(f'{data_type}-{instrument}-{self.time}.csv', mode='a', header=False)

    def _add_args(self):
        self.parser.add_argument('--csv', type=bool)
        self.parser.add_argument('--aws', type=bool)
        return super()._add_args()

    def _process_callback(self, response: json):
        """Override this method to process the callback message

        Args:
            response (json): Contains the response message from the websocket.
        """

        # processes LOB data
        if 'params' in response.keys() and response['method'] == 'subscription':
            if response['params']['channel'] == 'book.BTC-PERPETUAL.none.10.100ms':

                timestamp = datetime.fromtimestamp(response['params']['data']['timestamp']/1000)
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

                orderbook = pd.DataFrame(data)
                #orderbook.set_index('timestamp')

                self._data['orderbook'] = pd.concat([self._data['orderbook'], orderbook], ignore_index=True, copy=False)
                print(self._data['orderbook'])
                #self._data = pd.merge_asof(self._data, orderbook, on='timestamp')
                
                instrument = response['params']['data']['instrument_name']

                if self.args.csv:
                    self.write_csv(self._data['orderbook'], 'orderbook', instrument)    

            if response['params']['channel'] == 'ticker.BTC-PERPETUAL.raw':
                
                stats = response['params']['data']['stats']
                timestamp = datetime.fromtimestamp(response['params']['data']['timestamp']/1000)
                volume = stats['volume_usd']
                open_interest = response['params']['data']['open_interest']

                data = dict(timestamp=[timestamp], volume=[volume], open_interest=[open_interest])
                ticker = pd.DataFrame(data)
                
                #print(ticker.dtypes)
                #print(self.data)
                self._data['ticker'] = pd.concat([self._data['ticker'], ticker], ignore_index=True, copy=False)
                print(self._data['ticker'])

                instrument = response['params']['data']['instrument_name']
                if self.args.csv:
                    self.write_csv(self._data['ticker'], 'ticker', instrument)

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

    stream = DataCollector(client_id, client_secret)
    stream.start()