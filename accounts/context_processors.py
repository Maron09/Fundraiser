from django.conf import settings



def get_paystck_secret_key(request):
    """
    Context processor to add Paystack secret key to the context.
    """
    return {
        'PAYSTACK_SECRET_KEY': settings.PAYSTACK_SECRET_KEY,
    }