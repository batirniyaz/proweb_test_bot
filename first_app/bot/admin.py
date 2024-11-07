from django.contrib import admin

from .handlers_admin import send_admin_conf
from .models import BotUser, BotGroup


# Register your models here.


class BotUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'role')
    list_filter = ('language', 'role')
    search_fields = ('chat_id', 'username', 'first_name', 'last_name')
    actions = ['make_admin']

    def make_admin(self, request, queryset):
        queryset.update(role='admin')
        for user in queryset:
            send_admin_conf(user.chat_id)
        self.message_user(request, 'выбранные пользователи поднялись до админки')

    make_admin.short_description = 'Сделать админом'


class BotGroups(admin.ModelAdmin):
    list_display = ('chat_id', 'chat_link', 'course_name', 'group_language', 'group_graphic', 'group_time')
    list_filter = ('course_name', 'group_language', 'group_graphic', 'group_time')
    search_fields = ('chat_id', 'chat_link', 'course_name', 'group_language', 'group_graphic', 'group_time')


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(BotGroup, BotGroups)
