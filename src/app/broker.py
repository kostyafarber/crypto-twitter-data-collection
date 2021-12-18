from deribit import DeribitClient
import json
import os
from utils import get_api_keys

# get api keys
client_id, client_secret = get_api_keys("CLIENT_ID_DERIBIT_TESTNET", "CLIENT_SECRET_DERIBIT_TESTNET")


class Broker(DeribitClient):
    def __init__(self, client_id, client_secret, testnet=False) -> None:
        super().__init__(client_id, client_secret, testnet=testnet)

    def msg_account_summary(self, currency: str) -> str:
        """Sends msg to request account summary

        https://docs.deribit.com/#private-get_account_summary

        Args:
            currency (str): Currency ticker for account

        Returns:
            str: Returns the message once it is sent.
        """
        msg = {
                "jsonrpc" : "2.0",
                "method" : "private/get_account_summary",
                "id": 2515,
                "params" : {
                    "currency" : currency,
                    "extended" : True
                    }
                }

        self.ws.send(json.dumps(msg))

    def buy(self, instrument, amount, order_type):
        """
        generate a buy order

            https://docs.deribit.com/#private-buy

        Args:
            instrument (str): which instrument to buy
            amount (float): amount to buy
            order_type (str): order type
        """
        msg = {
                "jsonrpc" : "2.0",
                "id" : 5275,
                "method" : "private/buy",
                "params" : {
                    "instrument_name" : instrument,
                    "amount" : amount,
                    "type" : order_type
                            }
                }
        
        self.ws.send(json.dumps(msg))

    def _process_callback(self, response):
        # name = response['result']['system_name']
        # equity = response['result']['equity']

        # print(f"Hello {name}, your equity right now is: {equity}")
        print(response)

    def _on_open_message(self):
        #self.stream_instrument_info('BTC-PERPETUAL', '100ms')
        #self.buy('BTC-PERPETUAL', 10, 'market')
        #self.stream_user_portfolio('btc')
        self.get_position('BTC-PERPETUAL')
    def stream_instrument_info(self, instrument, interval):
        """stream user instrument account related info

        https://docs.deribit.com/#user-changes-instrument_name-interval

        Args:
            instrument (str): instrument name
        """

        # To subscribe to this channel:
        msg = {"jsonrpc": "2.0",
                "method": "private/subscribe",
                "id": 42,
                "params": {
                    "channels": [f"user.changes.{instrument}.{interval}"]}
                }

        self.ws.send(json.dumps(msg))

    def stream_user_portfolio(self, currency):
        
        msg =  {"jsonrpc": "2.0",
                "method": "private/subscribe",
                "id": 42,
                "params": {
                    "channels": [f"user.portfolio.{currency}"]}
                }

        self.ws.send(json.dumps(msg))

    def get_position(self, instrument):
        msg = {
                "jsonrpc" : "2.0",
                "id" : 404,
                "method" : "private/get_position",
                "params" : {
                    "instrument_name" : f"{instrument}"}
            }

        self.ws.send(json.dumps(msg))

if __name__ == "__main__":
    broker = Broker(client_id, client_secret, testnet=True)
    broker.start()
    

