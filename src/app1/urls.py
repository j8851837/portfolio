from django.urls import path
from django.http import HttpResponse

from . import views

urlpatterns = [
    path('', views.index),
    path('timeline/', views.timeline),
    path('set_reading_position/', views.set_reading_position),
    path('past_tweets/', views.past_tweets),
    path('set_like/', views.set_like),
    path('twitter_auth/', views.twitter_auth, name='twitter_auth'),
    path('sign_up/', views.sign_up),
    path('logout/', views.logout, name='logout'),
    path('status/', lambda request: HttpResponse()),
]

