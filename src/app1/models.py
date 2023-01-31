from django.db import models

class Users(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    top_tweet = models.CharField(max_length=20, null=True)
    tweet_30th = models.CharField(max_length=20)
    last_access = models.DateTimeField(null=True)
    needs_get_api = models.BooleanField(null=True)

class Tweets(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, to_field="user_id")
    tweet_id = models.CharField(max_length=20)
    tweet_user = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    text = models.CharField(max_length=255)
    reply = models.CharField(max_length=20, null=True)
    favorited = models.BooleanField()