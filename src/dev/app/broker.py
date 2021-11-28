from deribit import DeribitClient
import json
import os

client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]
exchange_version = 'wss://www.deribit.com/ws/api/v2/'

class Broker(DeribitClient):
    def msg_account_summary(self, currency: str) -> str:

        # authenticate
        #self._authentication()

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
    
    def _get_account_summary(self, response):
        pass

    def _process_callback(self, response):
        pass

    def _on_open_message(self):
        
        self.msg_account_summary('BTC')

if __name__ == "__main__":
    broker = Broker(client_id, client_secret, exchange_version)
    broker.start()
    

