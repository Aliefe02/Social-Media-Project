from rest_framework import serializers
from .models import *

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','username','email','password','first_name','last_name','about','profile_image']
        extra_kwargs={
            'password':{'write_only':True}
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class FilteredProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username','email','first_name','last_name','profile_image']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'
    
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_like
        fields = '__all__'

class UserGameSerializer(serializers.ModelSerializer):
    class Meta:
        model =  UserGames
        fields = '__all__'
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Post_Comment
        fields = '__all__'
        