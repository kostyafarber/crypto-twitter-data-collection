import datetime
from binance import ThreadedWebsocketManager
import pandas as pd
import boto3
import sys

# obtain binance api keys from aws
ssm = boto3.client('ssm', region_name='ap-southeast-2')
response = ssm.get_parameters(Names=['binance-public-key', 'binance-api-secret'], WithDecryption=True)
api_key = response['Parameters'][0]["Value"]
api_secret = response['Parameters'][1]["Value"]

symbol = 'BTCUSDT'

order_book = pd.DataFrame()

# when to stop stream
time_delta = int(sys.argv[1])
stop_time = datetime.datetime.now()
stop_time = stop_time + datetime.timedelta(hours=time_delta)

def main():
    
    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    print("Connecting to socket...")
    twm.start()

    def handle_socket_message(msg):
    
        timestamp = datetime.datetime.fromtimestamp(msg['E']/1000)
        #stop_time = timestamp + datetime.timedelta(seconds=5)
        bids = msg['b']
        asks = msg['a']

        data = dict(timestamp=timestamp, bids=bids, asks=asks)
        global order_book

        df = pd.json_normalize(data)
        order_book = pd.concat([order_book, df], ignore_index=True)
        print(order_book)

        global stop_time

        if timestamp > stop_time:
                
            print("Closing Connection...")
            print("Saving " + symbol + ' order book data')
            file_path = f'{symbol}-{timestamp}.pkl'
            order_book.to_pickle(file_path)
            twm.stop()

            # save to s3
            s3 = boto3.client('s3')
            bucket = 'crypto-data-kos'
            s3.Object(bucket, f'data/{file_path}').put(Body=open(f'{file_path}', 'rb'))

        elif msg['e'] == 'error':

            # save log of error
            with open('log.txt', 'w') as log:
                log.write(msg['e'])
            
            # restart stream
            twm.stop(stream)
            twm.start()
            twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    stream = twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)
    
    twm.join()

if __name__ == "__main__":
    main()

