from dataclasses import dataclass
from datetime import datetime
from collections import deque
import yaml
import tweepy
import sys


class TwitterUser:

    def __init__(self, id_, username, name, followers_count, following_count, tweets, followers, following) -> None:

        self.id_ = id_
        self.username = username
        self.name = name
        self.followers_count = followers_count
        self.following_count = following_count
        self.tweets = tweets
        self.followers = followers
        self.following = following
        self.rank = 1


# parents = following
# children = followers

    def update_pagerank(self) -> float:

        temp_rank = 0

        for parent in self.following:
            temp_rank += parent.rank / parent.followers_count

        old_rank = self.rank
        self.rank = temp_rank

        return abs(old_rank - self.rank)
    

    def __str__(self) -> str:
        return f'''
        id: {self.id_},
        username: {self.username},
        name: {self.name},
        followers_count: {self.followers_count},
        following_count: {self.following_count},
        rank: {self.rank},
        self.followers : {self.followers}
        self.following : {self.following}
        
    '''


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

        self.client = tweepy.Client(access_token=self.twitter_auth_creds['ACCESS_TOKEN'],
                                    access_token_secret=self.twitter_auth_creds['ACCESS_TOKEN_SECRET'],
                                    consumer_key=self.twitter_auth_creds['COSUMER_KEY'],
                                    consumer_secret=self.twitter_auth_creds['CONSUMER_SECRET'],
                                    bearer_token=self.twitter_auth_creds['BEARER_TOKEN'],
                                    wait_on_rate_limit=True)

    def get_user_data_from_username(self, screen_name: str):

        print(f'now fetching for: {screen_name}')

        user_data = self.client.get_user(username=screen_name,
                                         user_fields=['public_metrics'])

        user_id = user_data.data.id

        return TwitterUser(
                            user_id,
                           user_data.data.username,
                           user_data.data.name,
                           user_data.data.public_metrics['followers_count'],
                           user_data.data.public_metrics['following_count'],
                           self.get_users_recent_tweets(user_id=user_id),
                           self.get_user_followers(user_id),
                           self.get_user_following(user_id)
                           )

    def get_users_recent_tweets(self, user_id, max_tweets=100):

        tweets = self.client.get_users_tweets(
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

                # domain_name = context['domain']['name']
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

    def get_user_followers(self, user_id):

        followers = self.client.get_users_followers(user_id,max_results=5)

        followers_list = []

        for follower in followers.data:
            followers_list.append(follower.username)

        return followers_list

    def get_user_following(self, user_id):

        following = self.client.get_users_following(user_id,max_results=5)

        following_list = []

        for follower in following.data:
            following_list.append(follower.username)

        return following_list

def generate_graph(username):
    
    twit = TwitterData(filename='twitter.yaml')

    users = deque([(username,0)])
    processed = []

    graph = []

    while len(users) > 0:

        user,level = users.popleft()
        
        if user in processed:
            continue
        
        user_data = twit.get_user_data_from_username(user)

        graph.append(user_data)

        if level < 2:
            users.extend((x,level+1) for x in user_data.followers)
            users.extend((x,level+1) for x in user_data.followers)

    return graph

if __name__ == '__main__':
    twit = TwitterData(filename='twitter.yaml')
    user = sys.argv[1].strip()
    # user1 = twit.get_user_data_from_username(user)
    # print(user1)
    g = generate_graph(user)

    print(g)
