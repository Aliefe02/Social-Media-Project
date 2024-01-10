from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import pytz
import uuid

class Profile(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    about = models.CharField(max_length=255,null=True)
    steamid = models.BigIntegerField(null=True)
    Personaname = models.CharField(max_length=100,null=True)
    ProfileURL = models.CharField(max_length=100,null=True)
    time_created_steam_account = models.BigIntegerField(null=True)
    profile_image = models.CharField(max_length=1000,default='https://res.cloudinary.com/dh3oyo4uz/image/upload/v1688826656/defaultprofile_qx3dgj.jpg')
    REQUIRED_FIELDS = []

class IP_count(models.Model):
    IP = models.CharField(max_length=30)
    username = models.CharField(max_length=50,null=True)
    count = models.IntegerField(default=1)
    timestamp = models.DateTimeField(default=timezone.now)

class BlockedIP(models.Model):
    IP = models.CharField(max_length=50)
    username = models.CharField(max_length=50,null=True)   
    timestamp = models.DateTimeField(default=timezone.now)

class Game(models.Model):
    game_name = models.CharField(max_length=300)
    app_id = models.IntegerField()

class Post(models.Model):
    postID = models.UUIDField(primary_key=True,default=uuid.uuid4)
    userID = models.IntegerField()
    username = models.CharField(max_length=50)
    profile_image =  models.CharField(max_length=1000,default='https://res.cloudinary.com/dh3oyo4uz/image/upload/v1688826656/defaultprofile_qx3dgj.jpg')
    url = models.CharField(max_length=1000)
    caption = models.CharField(max_length=200,null=True)
    game_name = models.CharField(max_length=300,null=True)    
    app_id = models.CharField(max_length=50, null=True)
    tags = models.CharField(max_length=1000, null=True)
    teammates = models.CharField(max_length=1000,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    number_of_likes = models.BigIntegerField(default=0)
    latest_comment = models.CharField(max_length=255,null=True)
    latest_comment_username = models.CharField(max_length=50,null=True)

class Post_like(models.Model):
    like_id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    username = models.CharField(max_length=50)
    postID = models.CharField(max_length=50)
    liked_at = models.DateTimeField(default=timezone.now)

class Post_Comment(models.Model):
    comment = models.CharField(max_length=255)
    username = models.CharField(max_length=50)
    profile_image = models.CharField(max_length=1000,default='https://res.cloudinary.com/dh3oyo4uz/image/upload/v1688826656/defaultprofile_qx3dgj.jpg')
    postID = models.CharField(max_length=50)
    comment_time = models.DateTimeField(default=timezone.now)
    

class Follower(models.Model):
    username = models.CharField(max_length=50)
    follower = models.CharField(max_length=50)
    following_start_date = models.DateTimeField(default=timezone.now)


class UserGames(models.Model):
    username = models.CharField(max_length=50)
    app_id = models.IntegerField()
    game_name = models.CharField(max_length=300)
    platform = models.CharField(max_length=100)

class Token(models.Model):
    username = models.CharField(max_length=50)
    token = models.CharField(max_length=300)
    timestamp = models.DateTimeField(default=timezone.now)