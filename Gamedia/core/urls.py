from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('signup',views.signup, name='signup'),
    path('signin',views.signin, name='signin'),
    path('logout',views.logout, name='logout'),
    path('uploadpost',views.uploadPost, name='uploadPost'),
    path('deletepost',views.DeletePost, name='DeletePost'),
    path('likepost',views.LikePost, name='likepost'),
    path('comment',views.Comment, name='comment'),
    path('comments',views.CommentList, name='comments'),
    path('postlikes',views.PostLikes, name='postlikes'),
    path('follow',views.Follow, name='Follow'),
    path('unfollow',views.Unfollow, name='Unfollow'),
    path('profile',views.Profile, name='Profile'),
    path('connectionResult',views.connectionResult,name='connectionResult'),
    path('steamlogin',views.login),
    path('callback',views.login_callback),
    path('settings',views.Settings, name='settings'),
    path('changeprofilepicture',views.ChangeProfilePicture, name='changeprofilepicture'),
    path('followers/',views.Followers, name='Followers'),
    path('following/',views.Following, name='Following'),
    path('<str:username>/followers',views.Followers, name='Followers'),
    path('<str:username>/following',views.Following, name='Following'),
    path('<str:username>/',views.UserByName, name='UserByName'),
]