from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import Answer, Question, Tag ,Profile


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
        print(f"Original text: '{text}'")  # Выводим исходное значение поля text

        if not text.strip():  # Убедитесь, что строка не пустая или состоит только из пробелов
            print("Validation failed: The answer is empty or only spaces.")  # Выводим сообщение об ошибке
            raise forms.ValidationError('The answer can not be empty!')
        
        print(f"Validated text: '{text.strip()}'")  # Выводим очищенную строку (без пробелов)
        return text


    def save(self, author, question):
        return Answer.objects.create(
            text=self.cleaned_data['text'],
            author=author,
            question=question
        )