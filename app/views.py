import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from .utils import *
from .models import *
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app.forms import LoginForm, RegisterForm, SettingsForm, AskForm, AnswerForm
from django.views.decorators.http import require_POST

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
        is_upvote = data.get('is_upvote')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = request.user
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return JsonResponse({"error": "Question not found"}, status=404)

    existing_like = QuestionLike.objects.filter(user=user, question=question).first()
    if existing_like:
        if existing_like.is_upvote == is_upvote:
            existing_like.delete()
        else:
            existing_like.is_upvote = is_upvote
            existing_like.save()
    else:
        QuestionLike.objects.create(user=user, question=question, is_upvote=is_upvote)

    likes_count = question.get_rating()
    return JsonResponse({'likes_count': likes_count})

@login_required
@require_POST
def answer_like(request, answer_id):
    try:
        data = json.loads(request.body)
        is_upvote = data.get('is_upvote')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = request.user
    answer = Answer.objects.filter(id=answer_id).first()
    if not answer:
        return JsonResponse({"error": "Answer not found"}, status=404)

    existing_like = AnswerLike.objects.filter(user=user, answer=answer).first()
    if existing_like:
        if existing_like.is_upvote == is_upvote:
            existing_like.delete()
        else:
            existing_like.is_upvote = is_upvote
            existing_like.save()
    else:
        AnswerLike.objects.create(user=user, answer=answer, is_upvote=is_upvote)

    likes_count = answer.get_rating()
    return JsonResponse({'likes_count': likes_count})
    
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
    if not answer:
        return JsonResponse({"error": "Answer not found"}, status=404)

    if correctness is not None:
        answer.correctness = correctness
    else:
        answer.correctness = not answer.correctness

    answer.save()
    return JsonResponse({'answer_correctness': answer.correctness})


