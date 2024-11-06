from django.db import models

# Create your models here.


class BotUser(models.Model):
    chat_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=3, default='ru')

    role = models.CharField(max_length=10, default='normal')

    def __str__(self):
        return self.username or str(self.chat_id), self.first_name


class BotGroup(models.Model):
    chat_id = models.CharField(max_length=100, unique=True)
    chat_name = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255)
    group_language = models.CharField(max_length=10)
    group_graphic = models.CharField(max_length=10)
    group_time = models.CharField(max_length=10)

    def __str__(self):
        return self.chat_id, self.chat_name