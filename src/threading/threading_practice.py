import os
from twitter import TwitterStreamer
from threading import Thread
from random import randint
import pandas as pd
from data_collector import DataCollector

# deribit
client_id = os.environ["CLIENT_ID_DERIBIT"]
client_secret = os.environ["CLIENT_SECRET_DERIBIT"]
exchange_version = 'wss://www.deribit.com/ws/api/v2/'

# twitter
bearer_token = os.environ['BEARER_TOKEN_TWITTER']
query_params = {'query': 'btc','tweet.fields': 'created_at'}


twitter = TwitterStreamer(bearer_token)
deribit = DataCollector(client_id, client_secret, exchange_version)


deribit.start()
twitter.start()

# while True:
#     data = pd.concat([twitter.tweet_df, deribit.orderbook])
#     print(data)






