from django.contrib import admin
from .models import BotUser


# Register your models here.


class BotUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'role')
    actions = ['make_admin']

    def make_admin(self, request, queryset):
        queryset.update(role='admin')
        for user in queryset:
            # admin_conf(user.chat_id)
            pass
        self.message_user(request, 'выбранные пользователи поднялись до админки')

