import datetime
import json
import time

from django.test import TestCase
from django.test.client import Client

from .models import Users, Tweets
from . import develop, twitter


class TwitterTestCase(TestCase):
    def setUp(self):
        user_info = Users.objects.create(
            user_id='test_user', 
            top_tweet='1618978394703544321', 
            tweet_30th='0', 
            needs_get_api=True
        )
        user_info.save()

        tweets_saved_in_sql = Tweets.objects.create(
            user_id = user_info,
            tweet_id = '1618978394703544321',
            tweet_user = '読売新聞オンライン',
            time = '2023-01-27 23:25:03',
            text = '新聞記事',
            reply = None,
            favorited = False
        )
        tweets_saved_in_sql.save()


    def test_get_api(self):
        access_token = develop.access_token_j
        access_token_secret = develop.access_token_secret_j
        api = twitter.preparation_use_api(access_token, access_token_secret)
        timeline = twitter.get_api(api, None)
        counter = len(timeline)
        self.assertGreater(counter, 90)


    def test_sql_save_last_api_access(self):
        user_info = Users.objects.get(user_id='test_user')
        last_access = datetime.datetime.now().astimezone()
        twitter.sql_save_last_api_access(user_info, last_access)
        user_info_after_save = Users.objects.get(user_id='test_user')
        self.assertEqual(last_access, user_info_after_save.last_access)


    def test_get_sql(self):
        user_id = 'test_user'
        tweets_saved_in_sql = Tweets.objects.filter(user_id=user_id)
        user_info = Users.objects.get(user_id=user_id)
        get_from_sql = twitter.get_sql(user_id, tweets_saved_in_sql, user_info)
        counter = len(get_from_sql)
        self.assertEqual(counter, 1)


    def test_adding_timeline_to_sql(self):
        timeline = {'1618978394703544321': {'user': '読売新聞オンライン', 
                                            'time': '2023-01-27 23:25:03', 
                                            'text': '新聞記事', 
                                            'reply': None, 
                                            'favorited': False}}
        user_id = 'test_user'
        twitter.adding_timeline_to_sql(timeline, user_id)
        tweets_saved_in_sql = Tweets.objects.filter(user_id=user_id)
        counter = Tweets.objects.count()
        self.assertEqual(counter, 2)


    def test_reading_position(self):
        user_id = 'test_user'
        top_tweet = '111'
        tweet_30th = '222'
        needs_get_api = True
        twitter.set_reading_position(user_id, top_tweet, tweet_30th, needs_get_api)
        get_sql_user = Users.objects.get(user_id=user_id)
        self.assertEqual(get_sql_user.top_tweet, top_tweet)
        self.assertEqual(get_sql_user.tweet_30th, tweet_30th)
        self.assertEqual(get_sql_user.needs_get_api, True)
    

    def test_index(self):
        c = Client()
        # ログイン前
        response = c.get('/', **{'HTTP_USER_AGENT': 'iphone'})
        self.assertEqual(response.status_code, 200)

        # ログイン後
        session = c.session
        session['access_token'] = 'token'
        session.save()
        response = c.get('/', **{'HTTP_USER_AGENT': 'android'})
        self.assertEqual(response.status_code, 200)


    def test_timeline(self):
        c = Client()
        session = c.session
        session['user_id'] = 'test_user'
        session['access_token'] = develop.access_token_j
        session['access_token_secret'] = develop.access_token_secret_j
        session.save()
        
        user_info = Users.objects.get(user_id='test_user')
        now = datetime.datetime.now().astimezone()

        # APIアクセスしない
        user_info.last_access = now
        user_info.save()
        response = c.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response), 2)

        # APIアクセスする
        user_info.last_access = now - datetime.timedelta(minutes=3)
        user_info.save()
        response = c.get('/timeline/')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertGreater(len(json_response['timeline']), 90)


    def test_set_reading_position(self):
        user_id = 'test_user'
        c = Client()
        session = c.session
        session['user_id'] = user_id
        session.save()

        url = '/set_reading_position/?top_tweet=111&tweet_30th=222&needs_get_api=False'
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        get_sql_user = Users.objects.get(user_id=user_id)
        self.assertEqual(get_sql_user.top_tweet, '111')
        self.assertEqual(get_sql_user.tweet_30th, '222')
        self.assertEqual(get_sql_user.needs_get_api, False)


    def test_past_tweets(self):
        user_id = 'test_user'
        c = Client()
        session = c.session
        session['user_id'] = user_id
        session['access_token'] = develop.access_token_j
        session['access_token_secret'] = develop.access_token_secret_j
        session.save()
        url = '/past_tweets/?bottomTweetId=1620344902188949506' # 正常取得
        response = c.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(json_response['timeline']), 90)
        self.assertGreater(Tweets.objects.count(), 90)

        url = '/past_tweets/?bottomTweetId=aaa' # エラーへ
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Twitter API Error', response.json())


    def test_like(self):
        user_id = 'test_user'
        c = Client()
        session = c.session
        session['user_id'] = user_id
        session['access_token'] = develop.access_token_j
        session['access_token_secret'] = develop.access_token_secret_j
        session.save()
        url = '/set_like/?id_to_like=1618978394703544321'

        access_token = develop.access_token_j
        access_token_secret = develop.access_token_secret_j
        api = twitter.preparation_use_api(access_token, access_token_secret)
        is_favorited = api.get_status(url.split('=')[1]).favorited
        tweets_saved_in_sql = Tweets.objects.get(
            user_id = 'test_user',
            tweet_id = '1618978394703544321',
        )
        tweets_saved_in_sql.favorited = is_favorited
        tweets_saved_in_sql.save()
        time.sleep(3)

        response = c.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['result_set_like'], not is_favorited)
        time.sleep(3)

        response = c.get(url)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['result_set_like'], is_favorited)
        

