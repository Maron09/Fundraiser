from django.contrib import admin
from .models import User, EmailOtp, PasswordResetToken





@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "full_name", "is_active", "is_staff", "is_admin")
    list_filter = ("is_active", "is_staff", "is_admin")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ()
    list_per_page = 20
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.admin_order_field = "user__first_name" 
    full_name.short_description = "Full Name"


@admin.register(EmailOtp)
class EmailOtpAdmin(admin.ModelAdmin):
    list_display = ("otp","created_at")
    ordering = ("-created_at",)
    filter_horizontal = ()
    list_per_page = 20


admin.site.register(PasswordResetToken)
