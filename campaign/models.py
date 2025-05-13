from django.db import models
from authentication.models import User
from django.utils import timezone
from django.utils.text import slugify
from cloudinary.models import CloudinaryField




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set slug if the object is being created
            super().save(*args, **kwargs)

        if not self.slug or str(self.id) not in self.slug:
            self.slug = f"{slugify(self.name)}-{self.id}"
            kwargs['force_update'] = True
            super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name



class Campaign(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="campaigns")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="campaigns")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    goal = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField("Campaign Image", blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        creating = not self.pk
        if creating:
            super().save(*args, **kwargs)  # Save to get the ID first

        if not self.slug or str(self.id) not in self.slug:
            self.slug = f"{slugify(self.title)}-{self.id}"
            # Save only if slug is updated
            super().save(update_fields=["slug"])
    
    def __str__(self):
        return self.title
    
    @property
    def remaining_days(self):
        if self.end_date:
            return (self.end_date - timezone.now()).days
        return None
    
    @property
    def total_raised(self):
        return self.donations.aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    @property
    def progress(self):
        return (self.total_raised / self.goal) * 100 if self.goal > 0 else 0
    
    @property
    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()



# class Donation(models.Model):
#     campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="donations")
#     donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     comment = models.TextField(blank=True, null=True)
#     donation_date = models.DateTimeField(auto_now_add=True)
#     is_anonymous = models.BooleanField(default=False)
    
    
#     def __str__(self):
#         donor_display = "Anonymous" if self.is_anonymous or not self.donor else self.donor.get_full_name
#         return f"{self.amount} to {self.campaign.title} by {donor_display}"