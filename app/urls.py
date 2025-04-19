from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('', index, name='index'), 
    path('hot/', hot, name='hot'),
    path('tag/<str:tag_name>/', tag_view, name='tag_view'),
    path('question/<int:question_id>/', question_view, name='question_view'),
    path('question/<int:question_id>/answer/', add_answer, name='add_answer'),
    path('login/', login, name='login'),  
    path('signup/', signup, name='signup'), 
    path('logout/', logout, name='logout'), 
    path('settings/', settings, name='settings'),  
    path('ask/', ask, name='ask'), 
    path('question_like/<int:question_id>/', question_like, name='question_like'),
    path('answer_like/<int:answer_id>/', answer_like, name='answer_like'),
    path('answer/rate_correct/<int:answer_id>/', rate_correct, name='rate_correct'),
    path('search/', search_view, name='search')
]