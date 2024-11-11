from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, Count, Q

class QuestionLike(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    is_upvote = models.BooleanField(default=True)
    class Meta:
        unique_together = ('question', 'user')

class AnswerLike(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    is_upvote = models.BooleanField(default=True)

    class Meta:
        unique_together = ('answer', 'user')

class QuestionManager(models.Manager):
    def get_new(self):
        return super().get_queryset().order_by('-date')
    
    def get_hot(self):
        return super().get_queryset().annotate(
            rating=Count('questionlike__is_upvote', filter=Q(questionlike__is_upvote=True)) -
                    Count('questionlike__is_upvote', filter=Q(questionlike__is_upvote=False))
        ).order_by('-rating')
    
class TagManager(models.Manager):  
    def get_popular(self):
        return super().get_queryset().annotate(
            popularity=Count('question')
        ).order_by('-popularity')

    
class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True, db_index=True)
    
    objects = TagManager()

    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.CharField(max_length=120, db_index=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    tags = models.ManyToManyField(Tag)

    objects = QuestionManager()

    def get_rating(self):
        upvotes = QuestionLike.objects.filter(question=self, is_upvote=True).count()
        downvotes = QuestionLike.objects.filter(question=self, is_upvote=False).count()
        return upvotes - downvotes
    
    def count_answers(self):
        return Answer.objects.filter(question=self).count()
    
    def __str__(self):
        return f"{self.title[:20]}{'...' if len(self.title) > 20 else ''} by {self.author.username}"

class Answer(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True) 
    correctness = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)
    
    def get_rating(self):
        upvotes = AnswerLike.objects.filter(answer=self, is_upvote=True).count()
        downvotes = AnswerLike.objects.filter(answer=self, is_upvote=False).count()
        return upvotes - downvotes
    
    def __str__(self):
        return f"for {self.question.title[:10]}{'...' if len(self.question.title) > 10 else ''} by {self.author.username}"
    
class UserManager(models.Manager):  
    def get_best(self):
        return super().get_queryset().annotate(
            answers=Count('user__answer')
        ).order_by('-answers')
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    avatar = models.ImageField(null=True, blank=True)

    objects = UserManager()
    
    def __str__(self):
        return self.user.username