from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': ('avatar',)}),
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
