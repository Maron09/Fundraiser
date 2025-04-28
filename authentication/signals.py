from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, EmailOtp, PasswordResetToken
from django.conf import settings
from django.core.mail import send_mail
from .utils import send_otp


@receiver(post_save, sender=User)
def create_otp(sender, instance, created, **kwargs):
    """"
    Signal to create an OTP when a user is created.
    """
    if created:
        otp, _ = EmailOtp.objects.get_or_create(user=instance)
        otp.generate_otp()
        send_otp(instance.email, otp.otp)



@receiver(post_save, sender=PasswordResetToken)
def send_password_reset_email(sender, instance, created, **kwargs):
    """""
    Send an email with the password reset token when a PasswordResetToken is created.
    """
    
    if created:
        base_url = getattr(settings, "SITE_URL", "http://localhost:8001")
        reset_link = f"{base_url}/auth/reset-password/{instance.token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email="noreply@example.com",
            recipient_list=[instance.user.email],
            fail_silently=False,
        )