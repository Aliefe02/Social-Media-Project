# Generated by Django 4.2 on 2023-07-16 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0016_alter_post_number_of_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='steamid',
            field=models.IntegerField(null=True),
        ),
    ]
