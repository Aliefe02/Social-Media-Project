# Generated by Django 4.2.2 on 2023-07-05 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0004_post_remove_profile_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='caption',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
