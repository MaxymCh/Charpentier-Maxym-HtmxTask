# Generated by Django 4.2.7 on 2023-12-12 16:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firsttuto', '0003_usertask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='users'
        ),
        migrations.AddField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(related_name='tasks', through='firsttuto.UserTask', to=settings.AUTH_USER_MODEL),
        ),
    ]
