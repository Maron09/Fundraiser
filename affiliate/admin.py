from django.contrib import admin
from .models import Affiliate, AffiliateEarnings, AffiliateWallet, AffiliateTransaction, AffiliateWithdrawalRequest



@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('user', 'referral_code', 'subaccount_code', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'referral_code')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20



@admin.register(AffiliateEarnings)
class AffiliateEarningsAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'donation', 'amount_earned', 'created_at')
    search_fields = ('affiliate__user__first_name', 'affiliate__user__last_name', 'donation__id')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20


@admin.register(AffiliateWallet)
class AffiliateWalletAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'balance', 'last_updated')
    search_fields = ('affiliate__user__first_name', 'affiliate__user__last_name')
    list_filter = ('last_updated',)
    ordering = ('-last_updated',)
    list_per_page = 20

@admin.register(AffiliateTransaction)
class AffiliateTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'timestamp')
    search_fields = ('wallet__affiliate__user__first_name', 'wallet__affiliate__user__last_name')
    list_filter = ('transaction_type', 'timestamp')
    ordering = ('-timestamp',)
    list_per_page = 20

@admin.register(AffiliateWithdrawalRequest)
class AffiliateWithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'amount', 'status')
    search_fields = ('affiliate__user__first_name', 'affiliate__user__last_name')
    ordering = ('-id',)
    list_per_page = 20
    list_filter = ('status',)
    actions = ['approve_withdrawal_requests']
    def approve_withdrawal_requests(self, request, queryset):
        for withdrawal in queryset:
            withdrawal.status = 'approved'
            withdrawal.save()
        self.message_user(request, "Selected withdrawal requests have been approved.")
        