import asyncio
import websockets
import json
import os

websocket.
client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]

class Broker():
    def __init__(self, client_id, client_secret) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.json = {
            "jsonrpc" : "2.0",
            "id" : 1,
            "method" : None,
        }

    def loop(self, api, request) -> str:
        response = asyncio.get_event_loop().run_until_complete(api(json.dumps(request)))    
        return response

    async def private_api(self, request):
        self.json['method'] = 'public/auth'
        self.json['params'] = {
                                    "grant_type" : "client_credentials",
                                    "client_id" : self.client_id,
                                    "client_secret" : self.client_secret}

        async with websockets.connect('wss://www.deribit.com/ws/api/v2/') as websocket:
            await websocket.send(json.dumps(self.json))
            while websocket.open:
                await websocket.recv()
                
                # send out the request after doing a public auth
                await websocket.send(request)
                response = await websocket.recv()
                response = json.loads(response)
                return response

    def connect_private(self):
        print('Authenticating...')
        response = json.loads(self.loop(self.private_api, self.json))

        if 'error' in response:
            print('Connection Failed')
        
        else:
            print('Success')

    def get_positions(self, currency, kind):

        options = {'currency': currency, 'kind': kind}

        self.json['params'] = options
        self.json['id'] = 2236
        self.json['method'] = 'private/get_positions'

        response = self.loop(self.private_api, self.json)
        
        return response
if __name__ == '__main__':

    broker = Broker(client_id, client_secret)
    response = broker.get_positions('BTC', 'future')    
    print(response)