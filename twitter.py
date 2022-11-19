from dataclasses import dataclass
from datetime import datetime
from collections import deque
import yaml
import tweepy
import sys
import asyncio

from tweepy.asynchronous import AsyncClient


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

        self.client = AsyncClient(access_token=self.twitter_auth_creds['ACCESS_TOKEN'],
                                access_token_secret=self.twitter_auth_creds['ACCESS_TOKEN_SECRET'],
                                consumer_key=self.twitter_auth_creds['COSUMER_KEY'],
                                consumer_secret=self.twitter_auth_creds['CONSUMER_SECRET'],
                                bearer_token=self.twitter_auth_creds['BEARER_TOKEN'],
                                wait_on_rate_limit=True)

    async def get_users_data_from_usernames(self, usernames: str):

        users_data = await self.client.get_users(usernames=usernames, user_fields=['public_metrics'])

        users = []

        print(users_data.data)

        for user in users_data.data:
            users.append(await self.get_twitter_user_from_user_data(user))

        return users

    async def get_user_data_from_username(self, screen_name: str):

        print(f'now fetching for: {screen_name}')

        user_data = await self.client.get_user(username=screen_name, user_fields=['public_metrics'])

        return await self.get_twitter_user_from_user_data(user_data)

        # user_id = user_data.data.id

        # recent_tweets = self.get_users_recent_tweets(user_id)
        # user_followers = self.get_user_followers(user_id)
        # user_following = self.get_user_following(user_id)

        # return TwitterUser(
        #     user_id,
        #     user_data.data.username,
        #     user_data.data.name,
        #     user_data.data.public_metrics['followers_count'],
        #     user_data.data.public_metrics['following_count'],
        #     await recent_tweets,
        #     await user_followers,
        #     await user_following
        # )

    async def get_twitter_user_from_user_data(self, user_data):

        print(f' rather epic: {user_data}')

        user_id = user_data.data['id']

        # recent_tweets = self.get_users_recent_tweets(user_id)
        user_followers = await self.get_user_followers(user_id)
        user_following = await self.get_user_following(user_id)

        return TwitterUser(
            user_id,
            user_data.data['username'],
            user_data.data['name'],
            user_data.data['public_metrics']['followers_count'],
            user_data.data['public_metrics']['following_count'],
            None,
            user_followers,
            user_following
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

    async def get_user_followers(self, user_id):

        followers = await self.client.get_users_followers(user_id, max_results=5)

        if not followers.data:
            return []

        followers_list = []

        for follower in followers.data:
            followers_list.append(follower.username)

        return followers_list

    async def get_user_following(self, user_id):

        following = await self.client.get_users_following(user_id, max_results=5)

        if not following.data:
            return []

        following_list = []

        for follower in following.data:
            following_list.append(follower.username)

        return following_list


async def generate_graph(username):

    twit = TwitterData(filename='twitter.yaml')

    users = [username]
    processed = []

    graph = []

    level = 0

    while len(users) > 0:

        users_f = filter(lambda x: x not in processed, users)

        q = ""

        for _user in users_f:
            q += _user.strip()+","

        q = q[:-1]

        print(f"query = {q}")

        users_data = await twit.get_users_data_from_usernames(q)

        graph.extend(users_data)

        users.clear()

        for user__ in users_data:

            print(f'appending followers of: {user__.username}')

            if level <= 2:
                users.extend([x for x in user__.followers])
                users.extend([x for x in user__.followers])

        processed.extend(users_f)

        level += 1

    return graph


async def main():
    twit = TwitterData(filename='twitter.yaml')
    user = sys.argv[1].strip()
    # user1 = twit.get_user_data_from_username(user)
    # print(user1)
    g = await generate_graph(user)

    for user in g:
        print(user)

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_until_complete(loop.create_task(main()))
