# Generated by Django 4.2 on 2023-08-06 15:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0025_blockedip_username_ip_count_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post_Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=50)),
                ('postID', models.CharField(max_length=50)),
                ('comment_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='latest_comment',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
