# Generated by Django 4.2 on 2023-07-15 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0015_post_like_rename_name_game_game_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='number_of_likes',
            field=models.BigIntegerField(default=0),
        ),
    ]
