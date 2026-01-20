from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy
from rest_framework.authtoken.models import TokenProxy

from .models import Subscription, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (gettext_lazy('Personal info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (gettext_lazy('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'user_permissions'
            ),
        }),
        (gettext_lazy('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
        ('Дополнительные поля', {'fields': ('avatar',)}),
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')
    filter_horizontal = ('user_permissions',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            content_types_to_exclude = ContentType.objects.filter(
                model__in=('group', 'permission', 'tokenproxy', 'token',)
            )
            kwargs['queryset'] = Permission.objects.exclude(
                content_type__in=content_types_to_exclude
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
