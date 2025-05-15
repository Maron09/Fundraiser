from django.db import models
from campaign.models import Campaign
from authentication.models import User







class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="donations")
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    donation_date = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    
    
    def __str__(self):
        donor_display = "Anonymous" if self.is_anonymous or not self.donor else self.donor.get_full_name
        return f"{self.amount} to {self.campaign.title} by {donor_display}"
