from django.contrib import admin
from .models import Campaign, Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)
    list_per_page = 10
    list_editable = ('slug',)


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'goal', 'image', 'start_date', 'end_date', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    list_filter = ('is_active', 'category')
    list_per_page = 10
    list_editable = ('goal', 'is_active')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Campaign, CampaignAdmin)
