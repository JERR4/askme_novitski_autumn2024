import json
from cent import Client, PublishRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from askme_novitski.settings import CENTRIFUGO_API_KEY, CENTRIFUGO_API_URL
from .utils import *
from .models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app.forms import *
from django.views.decorators.http import require_POST

from django.contrib.postgres.search import SearchVector, SearchQuery

def index(request):
    QUESTIONS = Question.objects.get_new()
    page = paginate(QUESTIONS, request)
    user=request.user
    if user.is_authenticated:
        for question in page.object_list:
            existing_like = QuestionLike.objects.filter(user=user, question=question).first()
            question.user_vote = existing_like.is_upvote if existing_like else None

    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,
                      'title': 'New Questions'
                  })


def hot(request):
    QUESTIONS = Question.objects.get_hot()
    page = paginate(QUESTIONS, request)
    user=request.user
    if user.is_authenticated:
        for question in page.object_list:
            existing_like = QuestionLike.objects.filter(user=user, question=question).first()
            question.user_vote = existing_like.is_upvote if existing_like else None


    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,
                      'title': 'Hot Questions'
                  })

def tag_view(request, tag_name):
    QUESTIONS = Question.objects.get_new().filter(tags__name=tag_name)
    page = paginate(QUESTIONS, request)
    user=request.user
    if user.is_authenticated:
        for question in page.object_list:
            existing_like = QuestionLike.objects.filter(user=user, question=question).first()
            question.user_vote = existing_like.is_upvote if existing_like else None

    
    return render(request, 'index.html', 
                  context={
                      'questions': page.object_list,
                      'page_obj': page,                      
                      'title': 'Tag: ' + tag_name,
                  })

def question_view(request, question_id):
    question = Question.objects.get(id=question_id)
    user=request.user

    ANSWERS = Answer.objects.filter(question__id=question_id).order_by('date')
    page = paginate(ANSWERS, request)

    if user.is_authenticated:
        existing_like = QuestionLike.objects.filter(user=user, question=question).first()
        question.user_vote = existing_like.is_upvote if existing_like else None

        for answer in page.object_list:
            existing_like = AnswerLike.objects.filter(user=request.user, answer=answer).first()
            answer.user_vote = existing_like.is_upvote if existing_like else None

    return render(request, 'question.html', 
                  context={
                      'question': question,
                      'page_obj': page,                      
                      'answers': page.object_list
                  })

def login(request):
    continue_url = request.GET.get('next', reverse('index'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(continue_url)
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'continue_url': continue_url})


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect(reverse('index'))
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def logout(request):
    auth.logout(request)
    current_url = request.META.get('HTTP_REFERER', '/')
    return redirect(current_url)

@login_required
def settings(request):
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':

        form = SettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            print("Form is valid")
            user = form.save()
            print("User data saved:", user.username, user.email)

            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                print("User re-authenticated successfully")
                auth.login(request, user)
                print("User logged in successfully")
                return redirect(reverse('index'))
            else:
                print("Re-authentication failed")
        else:
            print("Form errors:", form.errors)
    else:
        form = SettingsForm(instance=user)
        print("Initialized form for GET request")

    print("Rendering settings page")
    return render(request, 'settings.html', {'form': form})



@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return redirect(reverse('question_view', args=[question.id]))
    else:
        form = AskForm()
    
    return render(request, 'ask.html', {'form': form})

@login_required
def add_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            answer = form.save(author=request.user, question=question)

            answers = Answer.objects.filter(question=question)
            page = paginate(answers, request)

            client = Client(CENTRIFUGO_API_URL, CENTRIFUGO_API_KEY)
            publish_request = PublishRequest(
                channel=str(question_id),
                data={
                    "message": answer.text,
                    "answer_id": answer.id,
                    "correctness": answer.correctness,
                    "page_id": page.paginator.num_pages,
                    "avatar_url": answer.author.profile.avatar.url if answer.author.profile.avatar else None
                }
            )
            result = client.publish(publish_request)

            redirect_url = f"{question.get_absolute_url()}?page={page.paginator.num_pages}#answer-{answer.id}"
            return redirect(redirect_url)
        else:
            print("Form is not valid")
            redirect_url = question.get_absolute_url()
            return redirect(redirect_url)
    else:
        form = AnswerForm()

    return render(request, 'question.html', {'question': question, 'form': form})

from django.shortcuts import redirect

@login_required
@require_POST
def question_like(request, question_id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    data['question_id'] = question_id

    form = QuestionLikeForm(data)
    if form.is_valid():
        likes_count = form.save(user=request.user)
        return JsonResponse({'likes_count': likes_count})
    else:
        return JsonResponse({"error": form.errors}, status=400)

@login_required
@require_POST
def answer_like(request, answer_id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    data['answer_id'] = answer_id

    form = AnswerLikeForm(data)
    if form.is_valid():
        likes_count = form.save(user=request.user)
        return JsonResponse({'likes_count': likes_count})
    else:
        return JsonResponse({"error": form.errors}, status=400)
    
@login_required
@require_POST
def rate_correct(request, answer_id):
    try:
        data = json.loads(request.body)
        correctness = data.get('correctness')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = request.user
    answer = Answer.objects.filter(id=answer_id).first()
    if (answer.question.author.id != user.id):
        return JsonResponse({"error": "You are not the author"}, status=403)
    if not answer:
        return JsonResponse({"error": "Answer not found"}, status=404)

    if correctness is not None:
        answer.correctness = correctness
    else:
        answer.correctness = not answer.correctness

    answer.save()
    return JsonResponse({'answer_correctness': answer.correctness})

def search_questions(query):
    search_vector = SearchVector('title', 'text')
    search_query = SearchQuery(query)

    return Question.objects.annotate(search=search_vector).filter(search=search_query)

def search_view(request):
    query = request.GET.get('query', '')
    results = []
    
    if query:
        search_results = search_questions(query)
        results = [{'title': result.title, 'id': result.id} for result in search_results][:10]
    
    return JsonResponse({'results': results})
