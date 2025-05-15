from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'donor', 'amount', 'donation_date', 'is_anonymous')
    search_fields = ('campaign__title', 'donor__username', 'amount')
    list_filter = ('donation_date', 'is_anonymous')
    ordering = ('-donation_date',)
    list_per_page = 10
    list_editable = ('is_anonymous',)
