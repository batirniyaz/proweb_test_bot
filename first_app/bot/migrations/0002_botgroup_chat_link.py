# Generated by Django 5.1.3 on 2024-11-07 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='botgroup',
            name='chat_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
