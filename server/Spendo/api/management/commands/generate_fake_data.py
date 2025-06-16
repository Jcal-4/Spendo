from django.core.management.base import BaseCommand
from api.models import CustomUser, Income, IncomeType, Account, Transaction, TransactionType
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate fake users and incomes for testing.'
    
    # Command line arguments when calling file
    def add_arguments(self, parser):      
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--incomes', type=int, default=5, help='Number of incomes per user')
        parser.add_argument('--accounts', type=int, default=6, help='Number of accounts per user')
        parser.add_argument('--user_transactions', type=int, default=8, help='Number of transactions per user')

    # Handle method is the first to initiate when the file is called
    def handle(self, *args, **options):          
        users_count = options['users']
        incomes_per_user = options['incomes']
        accounts_per_user = options['accounts']
        transaction_per_user = options['user_transactions']
        occupations = ['Engineer', 'Teacher', 'Doctor', 'Artist', 'Developer', 'Designer']
        income_types = ['Salary', 'Bonus', 'Freelance', 'Investment', 'Gift']
        institutions = [
            'Checking', 'Savings', 'Investment', '401k', 'Trusts', 'Credit',
            'Money Market', 'IRA', 'Roth IRA', 'Brokerage', 'Health Savings Account',
            'Certificate of Deposit', 'Business Account', 'Joint Account', 'Custodial Account',
            'Education Savings', 'PayPal', 'Venmo', 'Cash App', 'Prepaid Card',
            'Mortgage', 'Auto Loan', 'Personal Loan', 'Line of Credit', 'Travel Account',
            'Retirement Account', 'SEP IRA', 'Simple IRA', 'Annuity', 'Foreign Currency Account'
        ]
        user_transactions = [
            'ubereats', 'postmates', 'internet', 'att', 'haircut', 'groceries', 'steam game',
            'rent', 'mortgage', 'electric bill', 'water bill', 'gas bill', 'phone bill',
            'netflix', 'spotify', 'amazon purchase', 'target', 'walmart', 'starbucks',
            'gym membership', 'insurance', 'car payment', 'public transport', 'medical bill',
            'prescription', 'movie tickets', 'restaurant', 'airline ticket', 'hotel stay',
            'taxi', 'rideshare', 'parking', 'tuition', 'school supplies', 'childcare',
            'pet supplies', 'donation', 'gift', 'clothing', 'electronics', 'furniture',
            'home improvement', 'subscription box', 'laundry', 'dry cleaning', 'coffee shop',
            'fast food', 'concert tickets', 'sports event', 'theme park', 'books', 'magazine subscription'
        ]

        # Create transaction types
        transaction_types = ['scheduled', 'one-time']
        transaction_type_records = list()
        for transaction in transaction_types:
            transaction_obj, created = TransactionType.objects.get_or_create(type=transaction)
            transaction_type_records.append(transaction_obj)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Transaction Type: {transaction_obj.type}'))
            else:
                self.stdout.write(self.style.WARNING(f'Found existing Transaction Type: {transaction_obj.type}'))
        
        # Create income_types
        income_types = ['Salary', 'Bonus', 'Freelance', 'Investment', 'Gift', 'Commission', 'Rental', 'Dividend', 'Allowance', 'Pension']
        income_type_records = list()
        for income_t in income_types:
            new_income_type, created = IncomeType.objects.get_or_create(income_type=income_t)
            income_type_records.append(new_income_type)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Income Type: {new_income_type}'))
            else:
                self.stdout.write(self.style.WARNING(f'Found existing Income Type: {new_income_type}'))
        
        # Create a User record (varrying on the amount requested or default)
        for i in range(users_count):
            custom_user, created = CustomUser.objects.get_or_create(
                email=f'user{i}@example.com',
                defaults={
                    'username': f'user{i}',
                    'first_name': f'First{i}',
                    'last_name': f'Last{i}',
                    'password': 'password',
                    'occupation': random.choice(occupations),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {custom_user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Found existing user: {custom_user.username}'))

            # For each User being created, create a related Income record
            for j in range(incomes_per_user):
                income = Income.objects.create(
                    amount = round(random.uniform(100, 5000), 2),
                    user=custom_user,
                    income_date = timezone.now().date(),
                    incometype = random.choice(income_type_records)
                )
                self.stdout.write(self.style.SUCCESS(f'  Added income: {income.incometype} (${income.amount})'))
            
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
