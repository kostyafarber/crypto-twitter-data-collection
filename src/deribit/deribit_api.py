import asyncio
import websockets
import json
import os
import datetime


client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]


msg = \
    {"jsonrpc": "2.0",
     "method": "public/subscribe",
     "id": 42,
     "params": {
        "channels": ["book.BTC-PERPETUAL.none.10.100ms"]}
    }


async def call_api(msg):

    #condition = 'book.BTC-PERPETUAL.none.10.100ms'

    async with websockets.connect('wss://www.deribit.com/ws/api/v2/') as websocket:
       await websocket.send(msg)
       #time.sleep(5)
       while True:
            response = await websocket.recv()
        # do something with the response...
            response = json.loads(response)

            print(response.items())
            
            #if 'result' in response:
                #print('Connection successful')
            
            #elif 'subscription' in response:
                #response = json.loads(response)
                #timestamp = datetime.datetime.fromtimestamp(response['params']['data']['timestamp']/1000)

                #print(timestamp)

            #else:
                #print("Failed to connect.")

def main(api):
    return asyncio.get_event_loop().run_until_complete(api)

if __name__ == '__main__':
    main(call_api(json.dumps(msg)))
