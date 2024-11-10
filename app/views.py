from django.http import HttpResponse
from django.shortcuts import render
from .utils import *


QUESTIONS = [
   {
    'id': i,
    'title': f'How to build a moon park {i} ?',
    'text': f'Lorem {i} ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'
   } for i in range(1,70)
]

ANSWERS = [
   {
    'id': i,
    'text': f'First of all {i} I would like to thank you for the invitation to participate in such a ... Russia is the huge territory which in many respects needs to be render habitable.'
   } for i in range(1,10)
]


def index(request):
    page = paginate(QUESTIONS, request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,
                      'title': 'New Questions'
                  })

def hot(request):
    page = paginate(list(reversed(QUESTIONS)), request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,                      
                      'title': 'Hot Questions'
                  })

def tag_view(request, tag_name):
    page = paginate(QUESTIONS, request)
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,                      
                      'title': 'Tag: ' + tag_name,
                  })

def question_view(request, id):
    page = paginate(ANSWERS, request)
    return render(request, 'question.html', 
                  context={
                      'question': QUESTIONS[id],
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

