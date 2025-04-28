from django.db import models
from .managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
import random
from datetime import timedelta
from cloudinary.models import CloudinaryField
import uuid





class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=255, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last Name"))
    
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined"))
    last_login = models.DateTimeField(auto_now=True, verbose_name=_("Last Login"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Is Staff"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Is Admin"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("Is Superuser"))
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()
    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        super().save(*args, **kwargs)



class EmailOtp(models.Model):
    """
    Model to store email OTPs.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp")
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp}"
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        otp_code = str(random.randint(100000, 999999))
        self.otp = otp_code
        self.created_at = now()
        self.save()
    
    def is_valid(self):
        return now() < self.created_at + timedelta(minutes=5)


class PasswordResetToken(models.Model):
    """"
    Model to store password reset tokens.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return(now() - self.created_at).total_seconds() > 1800
