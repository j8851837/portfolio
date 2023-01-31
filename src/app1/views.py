import json
import re
import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import tweepy

from .models import Users, Tweets
from . import twitter, develop

CONSUMER_KEY = develop.CONSUMER_KEY
CONSUMER_SECRET = develop.CONSUMER_SECRET
CALLBACK_URL = 'http://localhost:8000/sign_up' # ローカル環境
TOP_PAGE = 'http://localhost:8000/' # ローカル環境

def index(request):
    user_agent  = request.META.get('HTTP_USER_AGENT')
    is_mobile = re.search('android|iphone', user_agent.lower())
    if 'access_token' in request.session:
        login = True
    else:
        login = False
    return render(request, 'with_template/index.html', 
                  {'login':login, 'is_mobile':bool(is_mobile)})


def timeline(request):
    user_id = request.session['user_id']
    user_info = Users.objects.get(user_id=user_id)
    tweets_saved_in_sql = Tweets.objects.filter(user_id=user_id)
    timeline = {}
    response = {}

    timeline.update(twitter.get_sql(user_id, tweets_saved_in_sql, user_info))
   
    if user_info.last_access:
        now = datetime.datetime.now().astimezone()
        time_elapsed = now - user_info.last_access
        if time_elapsed > datetime.timedelta(minutes=2):
            update_required = True
        else:
            update_required = False
    else:
        update_required = True
    if update_required and user_info.needs_get_api:
        api = twitter.preparation_use_api(request.session['access_token'], 
                                          request.session['access_token_secret'])
        try:
            timeline.update(twitter.get_api(api, None))
            last_access = datetime.datetime.now().astimezone()
            twitter.sql_save_last_api_access(user_info, last_access)
        except:
            response['Twitter API Error'] = 'Twitter API Error'

    if tweets_saved_in_sql:
        tweets_saved_in_sql.delete()
    twitter.adding_timeline_to_sql(timeline, user_id)

    response['timeline'] = timeline
    if user_info.top_tweet:
        response['topTweet'] = user_info.top_tweet

    return JsonResponse(response)


def set_reading_position(request):
    user_id = request.session['user_id']
    top_tweet = request.GET['top_tweet']
    tweet_30th = request.GET['tweet_30th']
    needs_get_api = request.GET['needs_get_api']
    response = {}
    try: 
        if int(top_tweet) < 99999999999999999999 and\
        int(tweet_30th) < 99999999999999999999 and\
        len(needs_get_api) < 6: # 不正な値でないか確認
            twitter.set_reading_position(user_id, top_tweet, tweet_30th, needs_get_api)
            response['result'] = 'reading position update succsess.'
    except:
        print('---------EROOR in set_reading_position---------')
    return JsonResponse(response)


def past_tweets(request):
    bottom_tweet_id = request.GET['bottomTweetId']
    response = {}
    try:
        if int(bottom_tweet_id) < 99999999999999999999: # 不正な値でないか確認
            api = twitter.preparation_use_api(request.session['access_token'], 
                                              request.session['access_token_secret'])
            max_id = str(int(bottom_tweet_id)-1)
            timeline = twitter.get_api(api, max_id)
            twitter.adding_timeline_to_sql(timeline, request.session['user_id'])
            response['timeline'] = timeline
    except:
            response['Twitter API Error'] = 'Twitter API Error'
    return JsonResponse(response)


def set_like(request):
    id_to_like = request.GET['id_to_like']
    if int(id_to_like) < 99999999999999999999: # 不正な値でないか確認
        tweet_saved_in_sql = Tweets.objects.get(user_id=request.session['user_id'], 
                                                tweet_id=id_to_like)
        api = twitter.preparation_use_api(request.session['access_token'], 
                                            request.session['access_token_secret'])
        if tweet_saved_in_sql.favorited == False:
            result_set_like = api.create_favorite(int(id_to_like))
            tweet_saved_in_sql.favorited = True
            tweet_saved_in_sql.save()
        else:
            result_set_like = api.destroy_favorite(int(id_to_like))
            tweet_saved_in_sql.favorited = False
            tweet_saved_in_sql.save()
        response_result = {'result_set_like' : result_set_like.favorited}
    return JsonResponse(response_result)


def twitter_auth(request):
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        redirect_url = auth.get_authorization_url()
        request.session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except:
        return render(request, 'with_template/error.html', {'url':TOP_PAGE})


def sign_up(request):
    try:
        token = request.session['request_token']
        del request.session['request_token']
        verifier = request.GET['oauth_verifier']
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        auth.request_token = token
        auth.get_access_token(verifier)

        api = tweepy.API(auth)
        user_id = api.verify_credentials().id_str
        if not Users.objects.filter(user_id=user_id):
            Users.objects.create(user_id=user_id, tweet_30th='0', needs_get_api=True)
        
        request.session.cycle_key()
        request.session['access_token'] = auth.access_token
        request.session['access_token_secret'] = auth.access_token_secret
        request.session['user_id'] = user_id

        return redirect('/')
    except:
        return render(request, 'with_template/error.html', {'url':TOP_PAGE}) 


def logout(request):
    request.session.clear()
    return redirect('/')