from django.core.management.base import BaseCommand
from ...models import User, Profile, Question, Answer, Tag, QuestionLike, AnswerLike
import random
from datetime import datetime, timedelta
from django.db import transaction

class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения сущностей')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        self.stdout.write('Создание пользователей...')
        users = [
            User(
                username=f'user{i}',
                email=f'user{i}@email.com',
                password='123'
            )
            for i in range(1, ratio + 1)
        ]
        User.objects.bulk_create(users)
        users = list(User.objects.all())
        self.stdout.write('Пользователи успешно созданы.')

        self.stdout.write('Создание профилей...')
        profiles = [Profile(user=user) for user in users]
        Profile.objects.bulk_create(profiles)
        self.stdout.write('Профили успешно созданы.')

        self.stdout.write('Создание тегов...')
        tags = [Tag(name=f'tag{i}') for i in range(1, ratio + 1)]
        Tag.objects.bulk_create(tags)
        self.stdout.write(f'{len(tags)} тегов успешно создано.')

        self.stdout.write('Создание вопросов...')
        now = datetime.now()
        questions = [
            Question(
                title=f'Question{i}',
                text=f'Lorem {i} ipsum dolor sit amet, consectetuer adipiscing elit...',
                author=random.choice(users),
                date=now - timedelta(days=random.randint(0, 365))
            )
            for i in range(1, ratio * 10 + 1)
        ]
        Question.objects.bulk_create(questions)
        questions = list(Question.objects.all())
        self.stdout.write('Вопросы успешно созданы.')
        question_tag_relations = []

        self.stdout.write('Добавление тегов к вопросам...')
        for question in questions:
            selected_tags = random.sample(tags, random.randint(1, 5))
            for tag in selected_tags:
                question_tag_relations.append(
                    Question.tags.through(question_id=question.id, tag_id=tag.id)
                )
        Question.tags.through.objects.bulk_create(question_tag_relations)
        self.stdout.write('Теги успешно добавлены к вопросам.')

        self.stdout.write('Создание ответов...')
        answers = [
            Answer(
                text=f'Answer {i} text example...',
                author=random.choice(users),
                question=random.choice(questions),
                date=now - timedelta(days=random.randint(0, 365))
            )
            for i in range(1, ratio * 100 + 1)
        ]
        Answer.objects.bulk_create(answers)
        self.stdout.write('Ответы успешно созданы.')

        self.stdout.write('Создание оценок вопросов...')
        question_likes = []
        existing_likes = set(
            QuestionLike.objects.values_list("question_id", "user_id")
        )
        for _ in range(1, ratio * 150 + 1):
            question = random.choice(questions)
            user = random.choice(users)
            if (question.id, user.id) not in existing_likes:
                question_likes.append(
                    QuestionLike(
                        question=question,
                        user=user,
                        is_upvote=random.choice([True, False])
                    )
                )
                existing_likes.add((question.id, user.id))

        batch_size = 1000
        for i in range(0, len(question_likes), batch_size):
            QuestionLike.objects.bulk_create(question_likes[i:i + batch_size])
        self.stdout.write('Оценки вопросов успешно созданы.')

        self.stdout.write('Создание оценок ответов...')
        answer_likes = []
        existing_answer_likes = set(
            AnswerLike.objects.values_list("answer_id", "user_id")
        )
        for _ in range(1, ratio * 150 + 1):
            answer = random.choice(answers)
            user = random.choice(users)
            if (answer.id, user.id) not in existing_answer_likes:
                answer_likes.append(
                    AnswerLike(
                        answer=answer,
                        user=user,
                        is_upvote=random.choice([True, False])
                    )
                )
                existing_answer_likes.add((answer.id, user.id))

        batch_size = 1000
        for i in range(0, len(answer_likes), batch_size):
            AnswerLike.objects.bulk_create(answer_likes[i:i + batch_size])

        self.stdout.write('Оценки ответов успешно созданы.')


        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
