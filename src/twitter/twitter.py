import socket
import json
import os
import requests
import datetime
import pandas as pd

# request to get credentials at http://apps.twitter.com
bearer_token = os.environ['BEARER_TOKEN_TWITTER']

class TwitterStreamer():
    def __init__(self, bearer_token) -> str:
        
        self.bearer_token = bearer_token
        self.tweet_df = pd.DataFrame()

    def OAuthBearer(self, request):
        """Generates the OAuthBearer for the subsequent requests

        Args:
            request (request_like): request

        Returns:
            request: request
        """
        request.headers['Authorization'] = 'Bearer ' + self.bearer_token
        return request

    def run(self):
        with requests.get("https://api.twitter.com/2/tweets/search/stream", auth=self.OAuthBearer) as r:
            while True:
                if r.status_code != 200:
                    print("Cannot get rules (HTTP {}): {}".format(r.status_code, r.text))
                    #break   
                    
                print(r.content)
                #for response_line in r.iter_lines():
                    #if response_line:
                        #json_response = json.loads(response_line)
                        #print(json.dumps(json_response, indent=4, sort_keys=True))

    def get_tweet(self, query):
        response = requests.get("https://api.twitter.com/2/tweets/search/recent", auth=self.OAuthBearer, params=query)
        
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

    def set_rules(self, rules: dict) -> str:
        """This function sets the rules that define what the client uses to search for tweets.

            https://api.twitter.com/2/tweets/search/stream/rules

        Args:
            rules (dict): A dictionary which sets out the rules:
        
        Returns:
            json: response object 

        Example:
            >>> rules = {"value": "dog has:images", "tag": "dog pictures"}
            >>> client.get_stream(rules)

        """

        payload = {"add": rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.OAuthBearer,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))

    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=self.OAuthBearer
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))
        return response.json()

    def delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self.OAuthBearer,
            json=payload
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        print(json.dumps(response.json()))
     
if __name__ == '__main__':
    query_params = {'query': 'btc','tweet.fields': 'created_at'}

    stream = TwitterStreamer(bearer_token)
    rules = stream.get_rules()
    stream.set_rules()
    pd.DataFrame()
    #stream.delete_all_rules(rules)
    #print(rules)
    #test = '{"data": [{"id": "1461819926709104640", "value": "dog has:images", "tag": "dog pictures"}, {"id": "1461819926709104641", "value": "cat has:images -grumpy", "tag": "cat pictures"}], "meta": {"sent": "2021-11-20T02:05:47.875Z", "result_count": 2}}'
    