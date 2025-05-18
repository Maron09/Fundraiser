from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Affiliate,  AffiliateWallet



@receiver(post_save, sender=Affiliate)
def create_affiliate_wallet(sender, instance, created, **kwargs):
    """
    Create an AffiliateWallet instance when a new Affiliate is created.
    """
    if created:
        AffiliateWallet.objects.create(affiliate=instance)
        print(f"Affiliate wallet created for {instance.user.get_full_name}")
    else:
        # If the Affiliate already exists, update the wallet if needed
        instance.wallet.save()
        print(f"Affiliate wallet updated for {instance.user.get_full_name}")