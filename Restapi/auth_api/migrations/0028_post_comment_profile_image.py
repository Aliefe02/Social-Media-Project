# Generated by Django 4.2 on 2023-08-18 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0027_post_latest_comment_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='post_comment',
            name='profile_image',
            field=models.CharField(default='https://res.cloudinary.com/dh3oyo4uz/image/upload/v1688826656/defaultprofile_qx3dgj.jpg', max_length=1000),
        ),
    ]
