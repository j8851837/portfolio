import datetime
import json

import tweepy

from .models import Users, Tweets
from . import develop

CONSUMER_KEY = develop.CONSUMER_KEY
CONSUMER_SECRET = develop.CONSUMER_SECRET
CALLBACK_URL = 'http://localhost:8000/sign_up'


def preparation_use_api(access_token, access_token_secret):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def get_api(api, max_id):
    get_from_api = {}
    tweets = api.home_timeline(count=200, max_id=max_id, tweet_mode='extended')
    for tweet_element in tweets:
        tweet = {}
        tweet['user'] = tweet_element.user.name
        time = tweet_element.created_at + datetime.timedelta(hours=9)
        tweet['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        tweet['text'] = tweet_element.full_text
        tweet['reply'] = tweet_element.in_reply_to_user_id_str
        tweet['favorited'] = tweet_element.favorited
        get_from_api[tweet_element.id_str] = tweet
    return get_from_api


def sql_save_last_api_access(user_info, last_access):
    last_access = last_access
    user_info.last_access = last_access
    user_info.save()


def get_sql(user_id, tweets_saved_in_sql, user_info):
    get_from_sql = {}
    
    if tweets_saved_in_sql:
        for tweet_element in tweets_saved_in_sql:
            if int(tweet_element.tweet_id) >= int(user_info.tweet_30th):
                tweet = {}
                tweet['user'] = tweet_element.tweet_user
                tweet['time'] = tweet_element.time
                tweet['text'] = tweet_element.text
                tweet['reply'] = tweet_element.reply
                tweet['favorited'] = tweet_element.favorited
                get_from_sql[tweet_element.tweet_id] = tweet
    return get_from_sql


def adding_timeline_to_sql(timeline, user_id):
    user_info = Users.objects.get(user_id=user_id)
    tweets_add_sql = []
    for key_tweet_id in timeline:
        tweet = Tweets(
            user_id = user_info,
            tweet_id = key_tweet_id,
            tweet_user = timeline[key_tweet_id]['user'],
            time = timeline[key_tweet_id]['time'],
            text = timeline[key_tweet_id]['text'],
            reply = timeline[key_tweet_id]['reply'],
            favorited = timeline[key_tweet_id]['favorited']
        )
        tweets_add_sql.append(tweet)
    Tweets.objects.bulk_create(tweets_add_sql) 


def set_reading_position(user_id, top_tweet, tweet_30th, needs_get_api):
    user_info = Users.objects.get(user_id=user_id)
    user_info.top_tweet = top_tweet
    user_info.tweet_30th = tweet_30th
    user_info.needs_get_api = needs_get_api
    user_info.save()
