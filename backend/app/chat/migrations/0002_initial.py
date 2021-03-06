# Generated by Django 3.2.9 on 2022-02-22 14:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='유저'),
        ),
        migrations.AddField(
            model_name='chat',
            name='user_set',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='참여자'),
        ),
    ]
