from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
    path('', index, name='index'), 
    path('hot/', hot, name='hot'),
    path('tag/<str:tag_name>/', tag_view, name='tag_view'),
    path('question/<int:question_id>/', question_view, name='question_view'), 
    path('login/', login, name='login'),  
    path('signup/', signup, name='signup'),  
    path('settings/', settings, name='settings'),  
    path('ask/', ask, name='ask'), 
]