from django.core.management.base import BaseCommand, CommandError
from firsttuto.models import Task
from django.contrib.auth import get_user_model
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generate random tasks and add them to the database'

    def add_arguments(self, parser):
        parser.add_argument('num_tasks', type=int, help='Number of tasks to generate')

    def handle(self, *args, **options):
        num_tasks = options['num_tasks']
        fake = Faker('fr_FR')  # Utilisation de faker en francais


        for i in range(num_tasks):
            description = fake.sentence(nb_words=10)
            user = get_user_model().objects.order_by('?').first()

            task = Task(description=description+" "+str(i))
            task.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {num_tasks} tasks'))

