from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.core.validators import EmailValidator
from .models import Answer, Question, Tag ,Profile, QuestionLike, AnswerLike


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        return self.cleaned_data['username'].lower().strip()


class RegisterForm(forms.ModelForm):
    password = forms.CharField()

    password_confirmation = forms.CharField()

    email = forms.EmailField(validators=[EmailValidator()],)

    username = forms.CharField()

    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'avatar')

    def clean(self):
        data = super().clean()

        if data.get('password') != data.get('password_confirmation'):
            self.add_error('password', 'Passwords do not match')
            self.add_error('password_confirmation', 'Passwords do not match')

        if User.objects.filter(email=data.get('email')).exists():
            self.add_error('email', 'Sorry, this email address has already been registered')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        if 'avatar' in self.cleaned_data:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return user

class SettingsForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField(validators=[EmailValidator()],)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'avatar')

    def clean(self):
        data = super().clean()

        current_email = self.instance.email
        new_email = data.get('email')

        if new_email != current_email:
            if User.objects.filter(email=new_email).exists():
                self.add_error('email', 'Sorry, this email address has already been registered')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()

        if 'avatar' in self.cleaned_data and self.cleaned_data['avatar']:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return user



class AskForm(forms.Form):
    title = forms.CharField(max_length=120)
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(required=False)
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
        return [tag.strip() for tag in tags.split(',')]

    def save(self, user):
        title = self.cleaned_data['title']
        text = self.cleaned_data['text']
        tags = self.cleaned_data['tags']

        tag_objects = []
        for tag_name in tags:
            tag_name = tag_name.lower()
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag_objects.append(tag)
        
        question = Question.objects.create(
            title=title,
            text=text,
            author=user,
        )

        question.tags.set(tag_objects)
        question.save()

        return question
    
class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your answer here...'}))

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if not text.strip():
            raise forms.ValidationError('The answer can not be empty!')
        return text


    def save(self, author, question):
        return Answer.objects.create(
            text=self.cleaned_data['text'],
            author=author,
            question=question
        )

class QuestionLikeForm(forms.Form):
    question_id = forms.IntegerField()
    is_upvote = forms.NullBooleanField()

    def save(self, user):
        question_id = self.cleaned_data['question_id']
        is_upvote = self.cleaned_data['is_upvote']

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

        return question.get_rating()
    
class AnswerLikeForm(forms.Form):
    answer_id = forms.IntegerField()
    is_upvote = forms.NullBooleanField()

    def save(self, user):
        answer_id = self.cleaned_data['answer_id']
        is_upvote = self.cleaned_data['is_upvote']

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

        return answer.get_rating()