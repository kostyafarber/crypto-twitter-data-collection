import time
import json
import hashlib
import hmac
import os
import websocket
from datetime import datetime, timedelta
import pandas as pd
import secrets
import boto3
import sys
import logging

# # obtain deribit api keys from aws
# ssm = boto3.client('ssm', region_name='ap-southeast-2')
# response = ssm.get_parameters(Names=['client_id_deribit', 'client_secret_deribit'], WithDecryption=True)
# client_id = response['Parameters'][0]["Value"]
# client_secret = response['Parameters'][1]["Value"]

client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]

exchange_version = 'wss://www.deribit.com/ws/api/v2/'

class DataCollector():
    def __init__(self, client_id, client_secret, exchange_version, enable_trace=False) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.exchange_version = exchange_version
        self.orderbook = pd.DataFrame()
        self.time = datetime.now()
        self.enable_trace = enable_trace
        self.expires_in = None
        self.heartbeat_requested_flag = 0
        self.heartbeat_set_flag = 0

        # Client Signature Authentication
        self.tstamp = str(int(time.time()) * 1000)
        self.data = ''
        self.nonce = secrets.token_urlsafe(10)
        self.base_signature_string = self.tstamp + "\n" + self.nonce + "\n" + self.data
        self.byte_key = client_secret.encode()
        self.message = self.base_signature_string.encode()
        self.signature = hmac.new(self.byte_key, self.message, hashlib.sha256).hexdigest()

    def on_message(self, ws, message):
        
        response = json.loads(message)
        
        if 'result' in response.keys() and response['result']['token_type'] == 'bearer':
            print(f'SUCCESSFULLY CONNECTED AT: {self.time.strftime("%Y-%m-%d %H:%M:%S")}\n')
            
            expires_in = response['result']['expires_in']
            self.expires_in = (self.time + timedelta(seconds=expires_in))
            print(f'AUTHENTICATION EXPIRES IN: {self.expires_in.strftime("%Y-%m-%d %H:%M:%S")}\n')

            print("Beginning data collection...")

        
        # respond to a test request
        if 'params' in response.keys() and response['method'] == 'heartbeat':                                    # noqa: E501
            ws_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "public/test",
                "params": {
                }
            }
            self.ws.send(json.dumps(ws_data))

        if 'params' in response.keys() and response['method'] == 'subscription':

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

            #data = dict(timestamp=timestamp, bids=bids, asks=asks)
            #print(net_ofi)
            print(f'{timestamp}: {net_ofi} {mid_price}')
            #df = pd.DataFrame.from_dict(data)
            #print(df)

            self.orderbook = pd.concat([self.orderbook, df], ignore_index=True)
            
            print(self.orderbook)
            
            instrument = response['params']['data']['instrument_name']

            # header on only the first entry
            if len(self.orderbook.index) == 1:
                self.orderbook.tail(1).to_csv(f'{instrument}-{self.time}.csv', mode='a')

            else:
                self.orderbook.tail(1).to_csv(f'{instrument}-{self.time}.csv', mode='a', header=False)    


        # heartbeat set success check and heartbeat response
        if 'params' in response.keys() and response['params']['type'] == 'heartbeat' and self.heartbeat_set_flag == 0:      # noqa: E501
            self.heartbeat_set_flag = 1
            print('Heartbeat Successfully Initiated at: ' + str(datetime.now().time().strftime('%H:%M:%S'))) 

    def on_open(self, ws):

        # Initial Authentication
        ws_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/auth",
            "params": {
                "grant_type": "client_signature",
                "client_id": self.client_id,
                "timestamp": self.tstamp,
                "nonce": self.nonce,
                "signature": self.signature,
                "data": self.data}
        }
        
        self.ws.send(json.dumps(ws_data))

         # Initiating Heartbeat
        if self.heartbeat_set_flag == 0 and self.heartbeat_requested_flag == 0:                                                     # noqa: E501
            self.heartbeat_requested_flag = 1
            print('Heartbeat Requested at: ' + str(datetime.now().time().strftime('%H:%M:%S')))                                     # noqa: E501
            ws_data = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "public/set_heartbeat",
                        "params": {
                            "interval": 60
                        }
                        }
            self.ws.send(json.dumps(ws_data))

        ws_data = {
            "jsonrpc": "2.0",
            "method": "public/subscribe",
            "id": 42,
            "params": {
                "channels": ["book.BTC-PERPETUAL.none.10.100ms"]}
        }

        self.ws.send(json.dumps(ws_data))

    def on_close(self, ws):
        #print('CONNECTION CLOSED AT: ' + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
        print('Attempting Reconnection at: ' + str(datetime.now().time().strftime('%H:%M:%S')))  # noqa: E501
        self.run()

    def run(self):
        #websocket.setdefaulttimeout(300)
        self.ws = websocket.WebSocketApp(self.exchange_version, on_message=self.on_message, on_open=self.on_open)
     
        if self.enable_trace:
            websocket.enableTrace(True)   

        while True:
            try:
                self.ws.run_forever()
            except:
                continue
if __name__ == '__main__':

    trace = False

    if len(sys.argv) >= 2:
        trace = sys.argv[1]

    engine = DataCollector(client_id, client_secret, exchange_version, trace)
    engine.run()