from django.core.management.base import BaseCommand
from api.models import CustomUser, Income, Account, Transaction, TransactionType
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate fake users and incomes for testing.'
    
    # Command line arguments when calling file
    def add_arguments(self, parser):      
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--incomes', type=int, default=5, help='Number of incomes per user')
        parser.add_argument('--accounts', type=int, default=2, help='Number of accounts per user')
        parser.add_argument('--user_transactions', type=int, default=3, help='Number of transactions per user')

    # Handle method is the first to initiate when the file is called
    def handle(self, *args, **options):          
        users_count = options['users']
        incomes_per_user = options['incomes']
        accounts_per_user = options['accounts']
        transaction_per_user = options['user_transactions']
        occupations = ['Engineer', 'Teacher', 'Doctor', 'Artist', 'Developer', 'Designer']
        income_types = ['Salary', 'Bonus', 'Freelance', 'Investment', 'Gift']
        institutions = ['Checking', 'Savings', "Investment", '401k', 'Trusts', 'Credit']
        user_transactions = ['ubereats', 'postmates', 'internet', 'att', 'haircut', 'groceries', 'steam game']

        # Create transaction types
        transaction_types = ['scheduled', 'one-time']
        transaction_type_records = list()
        for transaction in transaction_types:
            transaction = TransactionType.objects.create(
                type = transaction
            )
            transaction_type_records.append(transaction)
            self.stdout.write(self.style.SUCCESS(f'Created Transaction Type: {transaction.type}'))

        # Create a User record (varrying on the amount requested or default)
        for i in range(users_count):
            custom_user = CustomUser.objects.create(
                email=f'user{i}@example.com',
                username=f'user{i}',
                first_name=f'First{i}',
                last_name=f'Last{i}',
                password='password',
                occupation=random.choice(occupations),
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {custom_user.username}'))

            # For each User being created, create a related Income record
            for j in range(incomes_per_user):
                income = Income.objects.create(
                    income_type=random.choice(income_types),
                    amount=round(random.uniform(100, 5000), 2),
                    user=custom_user,
                    income_date=timezone.now().date(),
                )
                self.stdout.write(self.style.SUCCESS(f'  Added income: {income.income_type} (${income.amount})'))
            
            # For each User being created, create a related Account record
            for j in range(accounts_per_user):
                account = Account.objects.create(
                    balance = round(random.uniform(0, 10000), 2),
                    institution = random.choice(institutions),
                    user = custom_user
                )
                self.stdout.write(self.style.SUCCESS(f' Added Account: {account.institution}'))
                
            # For each User being created, create a related Transaction record
            for j in range(transaction_per_user):
                transaction = Transaction.objects.create(
                    name = random.choice(user_transactions),
                    payment = round(random.uniform(1,100), 2),
                    recurring = random.choice([True, False]),
                    user = custom_user,
                    transactiontype = random.choice(transaction_type_records)
                )
                self.stdout.write(self.style.SUCCESS(f' Added User Transaction: {transaction.name}'))

        self.stdout.write(self.style.SUCCESS('Fake data generation complete.'))
