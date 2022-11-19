from dataclasses import dataclass
import yaml
import tweepy
import sys
import asyncio
import re
from tweepy.asynchronous import AsyncClient

import jaccard_f as jacc

@dataclass(init=True, repr=True, frozen=True)
class TwitterUser:
    
    id_ : str
    username: str
    name: str
    tweets: str


@dataclass(init=True, repr=True, frozen=True)
class Tweet:

    id_: str
    text: str
    context_annotations: list


class TwitterData:

    def __init__(self, filename: str = "twitter-oauth.yaml") -> None:

        temp_twitter_auth_data = {}

        with open(filename, "r") as yamlfile:
            temp_twitter_auth_data = yaml.load(
                yamlfile, Loader=yaml.FullLoader)

        self.twitter_auth_creds = temp_twitter_auth_data['TWITTER']

        self.client = AsyncClient(access_token=self.twitter_auth_creds['ACCESS_TOKEN'],
                                access_token_secret=self.twitter_auth_creds['ACCESS_TOKEN_SECRET'],
                                consumer_key=self.twitter_auth_creds['COSUMER_KEY'],
                                consumer_secret=self.twitter_auth_creds['CONSUMER_SECRET'],
                                bearer_token=self.twitter_auth_creds['BEARER_TOKEN'],
                                wait_on_rate_limit=True)

    async def get_user_data_from_username(self, screen_name: str):

        print(f'now fetching for: {screen_name}')

        user_data = await self.client.get_user(username=screen_name, user_fields=['public_metrics'])

        user_id = user_data.data.id

        recent_tweets = self.get_users_recent_tweets(user_id)

        return TwitterUser(
            user_id,
            user_data.data.username,
            user_data.data.name,
            await recent_tweets
        )

    async def get_users_recent_tweets(self, user_id, max_tweets=100):

        tweets = await self.client.get_users_tweets(
            user_id, tweet_fields=['context_annotations'], max_results=max_tweets)

        final_tweets = []

        if not tweets.data:
            return []

        for tweet in tweets.data:

            tweet_context_annotations = []

            tweet_id = tweet.id
            tweet_text = tweet.text
            tweet_temp_context_annotations = tweet.context_annotations

            for context in tweet_temp_context_annotations:

                entity_name = context['entity']['name']

                if not entity_name in tweet_context_annotations:
                    tweet_context_annotations.append(entity_name)

            final_tweet = Tweet(
                tweet_id,
                tweet_text,
                tweet_context_annotations
            )

            final_tweets.append(final_tweet)

        return final_tweets

def transform_tweets_to_text(tweets: list):
    
    text = ""
    
    final_context_annotations = set()
    
    for tweet in tweets:
        text = text.replace("\n","")
        text+=tweet.text.strip() + " "
        
        for entity in tweet.context_annotations:
            final_context_annotations.add(entity.strip())
            
    for ca in final_context_annotations:
        text+= ca+" "
        
    text = re.sub(r'https?://\S+', '', text)
    
    text = text.replace("#",'')
    text = text.replace('@','')
    text = text.replace('(','')
    text = text.replace(')','')
            
    return text[:-1]          
        

async def main():
    twit = TwitterData(filename='twitter.yaml')
    user1 = sys.argv[1].strip()
    user2 = sys.argv[2].strip()
    
    twitter_user_1 = await twit.get_user_data_from_username(user1)
    twitter_user_2 = await twit.get_user_data_from_username(user2)
    
    tweets1 = transform_tweets_to_text(twitter_user_1.tweets)
    tweets2 = transform_tweets_to_text(twitter_user_2.tweets)
    
    print(tweets1)
    print('\n-----------------------------\n')
    print(tweets2)
    
    jacc.similarity_from_text(tweets1,tweets2)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_until_complete(loop.create_task(main()))
