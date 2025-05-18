from datetime import timezone
from django.db import models
from authentication.models import User
from donations.models import Donation




class Affiliate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate')
    referral_code = models.CharField(max_length=20, unique=True)
    subaccount_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name} - {self.referral_code}"
    



class AffiliateEarnings(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='earnings')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='affiliate_earnings')
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.affiliate.user.get_full_name} earned {self.amount_earned} from {self.donation.id}"


class AffiliateWallet(models.Model):
    affiliate = models.OneToOneField(Affiliate, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f" Wallet of {self.affiliate.user.get_full_name} - Balance: {self.balance}"



class AffiliateTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('EARNING', 'Earning'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    
    wallet = models.ForeignKey(AffiliateWallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    Description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.timestamp}"



class AffiliateWithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
    ]
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if self.status in ['approved', 'rejected'] and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.affiliate.user.get_full_name()} requested ₦{self.amount}"