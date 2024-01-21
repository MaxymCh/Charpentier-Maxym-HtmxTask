from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    pass

class Task(models.Model):
    description = models.CharField(max_length=128)
    users = models.ManyToManyField(User, related_name='tasks', through='UserTask')

class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    class Meta:
        ordering = ['order']