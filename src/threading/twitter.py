import socket
import json
import os
from threading import Thread
import requests
import datetime
import pandas as pd

bearer_token = os.environ['BEARER_TOKEN_TWITTER']

class TwitterStreamer(Thread):
    def __init__(self, bearer_token) -> str:
        super().__init__()
        self.bearer_token = bearer_token
        self.tweet_df = pd.DataFrame()

    def OAuthBearer(self, request):
         request.headers['Authorization'] = 'Bearer ' + self.bearer_token
         return request

    def run(self):
        with requests.get("https://api.twitter.com/2/tweets/search/stream", auth=self.OAuthBearer, stream=True) as r:
            while True:
                # response = r
                # print(json.dumps(r.json()))
                # return r.json()
                for response_line in r.iter_lines():
                    if response_line:
                        json_response = json.loads(response_line)
                        print(json.dumps(json_response, indent=4, sort_keys=True))        
            #while True:
                #if r.status_code != 200:
                    #print("Cannot get rules (HTTP {}): {}".format(r.status_code, r.text))
                    #break   

            #content = json.loads(r.content)
            #print(content)

    def get_tweet(self, query):
        query_params = {'query': 'btc','tweet.fields': 'created_at'}
        response = requests.get("https://api.twitter.com/2/tweets/search/recent", auth=self.OAuthBearer, params=query_params)
        
        if response.status_code != 200:
                    print("Cannot get rules (HTTP {}): {}".format(response.status_code, response.text))

        content = json.loads(response.content)
        data = content['data']

        date_df = []
        text_df = []

        for field in data:

            date = field['created_at']
            date_df.append(date)

            text = field['text']
            text_df.append(text)

            print("############-################")
            print(f"Tweeted at: {date}")
            print(text)
            print("############-################")
            print()

        df = pd.DataFrame(dict(timestamp=date_df, text=text_df))
        df.set_index('timestamp', inplace=True)

        self.tweet_df = df

        print(self.tweet_df)
        df.to_csv('test_twitter.csv')
        # for response_line in response.iter_lines():
        #     if response_line:
        #         json_response = json.loads(response_line)
        #         #print(json.dumps(json_response, indent=4, sort_keys=True))
        #         tweets = json_response['data']
        #         for text in tweets:
        #             print(text['text'])


    def get_rules(self):
        with requests.get("https://api.twitter.com/2/tweets/search/stream/rules", auth=self.OAuthBearer) as r:
            while True:
                if r.status_code != 200:
                    raise Exception("Cannot get rules (HTTP {}): {}".format(r.status_code, r.text))
        
                print(json.dumps(r.json()))
                return r.json()
     
if __name__ == '__main__':
    query_params = {'query': 'btc','tweet.fields': 'created_at'}

    stream = TwitterStreamer(bearer_token)
    stream.get_tweet(query=query_params)

    test = '{"data": [{"id": "1461819926709104640", "value": "dog has:images", "tag": "dog pictures"}, {"id": "1461819926709104641", "value": "cat has:images -grumpy", "tag": "cat pictures"}], "meta": {"sent": "2021-11-20T02:05:47.875Z", "result_count": 2}}'
    