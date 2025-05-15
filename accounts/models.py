from django.db import models
from authentication.models import User




class PaystackBank(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    code = models.CharField(max_length=10, unique=True)
    longcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)
    logo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.code})"




class UserBankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bank_accounts')
    bank = models.ForeignKey(PaystackBank, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'bank', 'account_number')
        
    def __str__(self):
        return f"{self.account_name or 'Unverified'} - {self.account_number} ({self.bank.name})"