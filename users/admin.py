from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "bio", "profile_picture", "address", "country", "state", "city")
    search_fields = ("user__username", "user__email")
    list_filter = ("country", "state", "city")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 20
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    full_name.short_description = "Full Name"


admin.site.register(UserProfile, UserProfileAdmin)
