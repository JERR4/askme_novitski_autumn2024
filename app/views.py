from django.http import HttpResponse
from django.shortcuts import render
from .utils import *
from .models import *


def index(request):
    QUESTIONS = Question.objects.get_new()
    page = paginate(QUESTIONS, request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,
                      'title': 'New Questions'
                  })

def hot(request):
    QUESTIONS = Question.objects.get_hot()
    page = paginate(QUESTIONS, request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,                      
                      'title': 'Hot Questions'
                  })

def tag_view(request, tag_name):
    QUESTIONS = Question.objects.get_new().filter(tags__name=tag_name)
    page = paginate(QUESTIONS, request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,                      
                      'title': 'Tag: ' + tag_name,
                  })

def question_view(request, question_id):
    question = Question.objects.get(id=question_id)
    ANSWERS = Answer.objects.filter(question__id=question_id)
    page = paginate(ANSWERS, request)
    return render(request, 'question.html', 
                  context={
                      'question': question,
                      'page_obj': page,                      
                      'answers': page.object_list
                  })

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'register.html')

def settings(request):
    return render(request, 'settings.html')

def ask(request):
    return render(request, 'ask.html')

