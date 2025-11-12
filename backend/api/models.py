from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    occupation = models.CharField(max_length=30, null=True, blank=True)
        
class IncomeType(models.Model):
    id = models.AutoField(primary_key=True)
    income_type = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
class Income(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    incometype = models.ForeignKey(IncomeType, on_delete=models.CASCADE, related_name='incomes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='incomes')
    income_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
class TransactionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
class Institution(models.Model):
    INSTITUTION_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('saving', 'Saving'),
        ('investing_retirement', 'Investing & Retirement'),
    ]
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=24, choices=INSTITUTION_TYPE_CHOICES)
class Account(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default="Account")
    balance = models.DecimalField(decimal_places=2, default=0.0, max_digits=10)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='accounts')
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    payment = models.DecimalField(decimal_places=2, default=0.0, max_digits=10)
    transaction_date = models.DateField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    note = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions', null=True)
    transactiontype = models.ForeignKey(TransactionType, on_delete=models.CASCADE, related_name='transactions')

class ChatKitThread(models.Model):
    """Store mapping of ChatKit thread_id to Django user_id for persistent user identification."""
    thread_id = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chatkit_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chatkit_threads'
        indexes = [
            models.Index(fields=['thread_id']),
            models.Index(fields=['user']),
        ]

class ChatKitUserSession(models.Model):
    """Store active user sessions for ChatKit - created on login, deleted on logout."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='chatkit_session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chatkit_user_sessions'
        indexes = [
            models.Index(fields=['user']),
        ]
    
