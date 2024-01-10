from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import *

urlpatterns = [
    path('register',csrf_exempt(RegisterView.as_view())),
    path('login',csrf_exempt(LoginView.as_view())),
    path("indexView", csrf_exempt(IndexView.as_view())),
    path("profileView", csrf_exempt(ProfileView.as_view())),
    path("userbynameView", csrf_exempt(UserByNameView.as_view())),
    path("followingView", csrf_exempt(FollowingView.as_view())),
    path("followersView", csrf_exempt(FollowersView.as_view())),
    path('user',csrf_exempt(UserView.as_view())),
    path('logout',csrf_exempt(LogoutView.as_view())),
    path('deleteuser',csrf_exempt(DeleteUserView.as_view())),
    path("uploadpost", csrf_exempt(UploadPost.as_view())),
    path("getposts", csrf_exempt(GetPosts.as_view())),
    path("getuserposts", csrf_exempt(GetUSerPosts.as_view())),
    path("getlikedposts", csrf_exempt(GetLikedPosts.as_view())),
    path("getpostlikes", csrf_exempt(GetPostLikes.as_view())),
    path("changeprofilepicture", csrf_exempt(ChangeProfilePicture.as_view())),
    path("deletepost", csrf_exempt(DeletePost.as_view())),
    path("follow", csrf_exempt(Follow.as_view())),
    path("unfollow", csrf_exempt(Unfollow.as_view())),
    path("getfollowers", csrf_exempt(GetFollowers.as_view())),
    path("getfollowing", csrf_exempt(GetFollowing.as_view())),
    path("getusers", csrf_exempt(GetUsers.as_view())),
    path("getfollowsuggestion", csrf_exempt(GetFollowSuggestion.as_view())),
    path("likepost", csrf_exempt(LikePost.as_view())),
    path("comment", csrf_exempt(Comment.as_view())),
    path("steamid", csrf_exempt(SteamID.as_view())),
    path("gamelist", csrf_exempt(GameList.as_view())),
    path("getprofile", csrf_exempt(GetProfile.as_view())),
    path("updateuser", csrf_exempt(UpdateUser.as_view())),
    path("getcomments", csrf_exempt(GetComments.as_view())),
]
