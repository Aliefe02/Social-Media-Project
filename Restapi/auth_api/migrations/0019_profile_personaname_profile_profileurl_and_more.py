# Generated by Django 4.2.2 on 2023-07-16 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0018_alter_profile_steamid'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='Personaname',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='ProfileURL',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='time_created_steam_account',
            field=models.BigIntegerField(null=True),
        ),
    ]
