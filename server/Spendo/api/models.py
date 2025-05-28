from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    occupation = models.CharField(max_length=30, null=True, blank=True)
        
class Income(models.Model):
    id = models.AutoField(primary_key=True)
    income_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='incomes')
    income_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'income'