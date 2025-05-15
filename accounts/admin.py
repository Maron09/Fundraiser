from django.contrib import admin
from .models import PaystackBank, UserBankAccount


@admin.register(PaystackBank)
class PaystackBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country', 'currency', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('country',)
    ordering = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    
@admin.register(UserBankAccount)
class UserBankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank', 'account_number', 'is_verified', 'created_at')
    search_fields = ('bank__name', 'account_number')
    list_filter = ('is_verified',)
    ordering = ('-created_at',)
    list_per_page = 20
