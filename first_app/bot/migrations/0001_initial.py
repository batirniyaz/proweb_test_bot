# Generated by Django 5.1.3 on 2024-11-07 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=100, unique=True)),
                ('chat_name', models.CharField(blank=True, max_length=255, null=True)),
                ('course_name', models.CharField(max_length=255)),
                ('group_language', models.CharField(max_length=10)),
                ('group_graphic', models.CharField(max_length=10)),
                ('group_time', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=100, unique=True)),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('language', models.CharField(default='ru', max_length=3)),
                ('role', models.CharField(default='normal', max_length=10)),
            ],
        ),
    ]
