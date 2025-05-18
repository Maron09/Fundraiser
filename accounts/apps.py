from django.apps import AppConfig
from django.core.management import call_command


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    # Change when production is ready use cron jobs
    # def ready(self):
    #     try:
    #         call_command("fetch_banks")
    #     except Exception as e:
    #         print(f"Error fetching banks: {e}")
    
    def ready(self):
        import affiliate.signals