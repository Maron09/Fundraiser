from django.core.management.base import BaseCommand
import paystack
from django.conf import settings
from accounts.models import PaystackBank
import pprint



class Command(BaseCommand):
    help = 'Fetches banks from Paystack and saves them to the database'
    
    def handle(self, *args, **kwargs):
        try:
            # paystack.api_key = settings.PAYSTACK_SECRET_KEY
            response = paystack.Verification.fetch_banks()
            if response.status:
                banks = response.data
                for bank in banks:
                    PaystackBank.objects.update_or_create(
                        code=bank['code'],
                        defaults={
                            'name': bank['name'],
                            'slug': bank.get('slug', ''),
                            'longcode': bank.get('longcode', ''),
                            'country': bank.get('country', 'NG'),
                            'currency': bank.get('currency', 'NGN'),
                            'logo': bank.get('logo', '')
                        }
                    )
                self.stdout.write(self.style.SUCCESS('Successfully fetched and saved banks from Paystack.'))
            else:
                self.stdout.write(self.style.ERROR('Failed to fetch banks from Paystack.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))