# Generated by Django 4.2.16 on 2024-12-25 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_answer_date_alter_question_date_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['title', 'text'], name='app_questio_title_75eb98_idx'),
        ),
    ]
