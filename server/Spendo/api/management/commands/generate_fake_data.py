from django.core.management.base import BaseCommand
from api.models import User, Income
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate fake users and incomes for testing.'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--incomes', type=int, default=5, help='Number of incomes per user')

    def handle(self, *args, **options):
        users_count = options['users']
        incomes_per_user = options['incomes']
        occupations = ['Engineer', 'Teacher', 'Doctor', 'Artist', 'Developer', 'Designer']
        income_types = ['Salary', 'Bonus', 'Freelance', 'Investment', 'Gift']

        for i in range(users_count):
            user = User.objects.create(
                email=f'user{i}@example.com',
                username=f'user{i}',
                first_name=f'First{i}',
                last_name=f'Last{i}',
                password='password',
                occupation=random.choice(occupations),
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

            for j in range(incomes_per_user):
                income = Income.objects.create(
                    income_type=random.choice(income_types),
                    amount=round(random.uniform(100, 5000), 2),
                    user=user,
                    income_date=timezone.now().date(),
                )
                self.stdout.write(self.style.SUCCESS(f'  Added income: {income.income_type} (${income.amount})'))

        self.stdout.write(self.style.SUCCESS('Fake data generation complete.'))
