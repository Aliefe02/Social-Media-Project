from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from .models import *
import jwt, datetime
from steam import Steam
from decouple import config
from django.utils import timezone
from datetime import timedelta

#   NOTES

# Deactivate cookie after logout


API_KEYS = ['Gamedia_first_api_key']

decode_key = 'gamedia'

def getuserfunc(username):
    user = Profile.objects.filter(username__exact=username).first()
    serializer = ProfileSerializer(user)
    return serializer.data

def getfollowersfunc(username):
    followers_objects = Follower.objects.filter(username__exact=username)
    serializer = FollowerSerializer(followers_objects,many=True).data
    follower_list = []
    
    for follower in serializer:
        follower_list.append(follower['follower'])
    
    followers = Profile.objects.filter(username__in=follower_list)
    follower_data = FilteredProfileSerializer(followers,many=True).data
    return {'follower_list':follower_list,'follower_data':follower_data}

def getfollowingfunc(username):
    following_objects = Follower.objects.filter(follower__exact=username)
    serializer = FollowerSerializer(following_objects,many=True).data
    following_list = []
    
    for follow in serializer:
        following_list.append(follow['username'])
    
    following = Profile.objects.filter(username__in=following_list)
    following_data = FilteredProfileSerializer(following,many=True).data
    return {'following_list':following_list,'following_data':following_data}

def getlikedpostsfunc(username):
    post_objects = Post_like.objects.filter(username__exact=username)
    posts = LikeSerializer(post_objects,many=True)
    liked_posts = []
    for post in posts.data:
        liked_posts.append(post['postID'])
    return liked_posts

def getpostsfunc(following_list):
        posts = Post.objects.filter(username__in=following_list).order_by('created_at')
        serializer = PostSerializer(posts,many=True)
        return serializer.data

def getfollowsuggestionfunc(following_list):
        users = Profile.objects.filter().exclude(username__in=following_list)
        users = ProfileSerializer(users,many=True).data
        return users

def ConnectSteamProfile(data):
    try:
        KEY = config("STEAM_API_KEY")
        ID = data['steamid']
        steam = Steam(KEY)
        steamProfile = steam.users.get_user_details(ID)
        user = Profile.objects.filter(username__exact=data['username']).first()
        user.steamid = ID
        user.Personaname = steamProfile['player']['personaname']
        user.ProfileURL = steamProfile['player']['profileurl']
        user.time_created_steam_account = steamProfile['player']['timecreated']
        user.save()

        return ''
    except Exception as e:
        return {'Problem':'Steam','Message':str(e)}
   

def UpdateLibrary(data):
    try:
        KEY = config("STEAM_API_KEY")
        ID = data['steamid']
        steam = Steam(KEY)

        user_games = steam.users.get_owned_games(ID)
        user_games = user_games['games']
        
        game_id = []
        games = Game.objects.all()
        game_list = GameSerializer(games,many=True).data

        for game_data in game_list:
            game_id.append(game_data['app_id'])

        for user_game in user_games:
            if user_game['appid'] not in game_id:
                game_id.append(user_game['appid'])
                new_game = Game.objects.create(game_name=user_game['name'],app_id=user_game['appid'])
                new_game.save()
        
        user_game_list_data = UserGames.objects.filter(username__exact=data['username'])  
        user_game_list = UserGameSerializer(user_game_list_data,many=True).data
        
        user_library = []
        if user_game_list is not None:
            for user_game_on_database in user_game_list:
                user_library.append(user_game_on_database['app_id'])

        for user_game in user_games:
            if user_game['appid'] not in user_library:
                new_game = UserGames.objects.create(username=data['username'],app_id=user_game['appid'],game_name=user_game['name'],platform='Steam')
        return ''
    except Exception as e:
        return {'Problem':'Steam','Message':str(e)}

def getuserpostsfunc(username):
    posts_data = Post.objects.filter(username__exact=username)
    posts = PostSerializer(posts_data,many=True).data
    return posts

class IndexView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = payload['username']
            user = getuserfunc(username)
            followers = getfollowersfunc(username)
            following = getfollowingfunc(username)
            likedposts = getlikedpostsfunc(username)
            list = following['following_list']
            list.append(username)
            posts = getpostsfunc(list)
            followsuggestion = getfollowsuggestionfunc(list)
            response.status_code = 200
            response.data = {'user':user,'followers':followers['follower_data'],'following':following['following_data'],
                             'likedposts':likedposts,'posts':posts,'followsuggestion':followsuggestion}
            return response
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response 

class ProfileView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = payload['username']
            user = getuserfunc(username)
            followers = getfollowersfunc(username)
            following = getfollowingfunc(username)
            likedposts = getlikedpostsfunc(username)
            userposts = getuserpostsfunc(username)
            response.status_code = 200
            response.data = {'user':user,'followers':followers['follower_data'],'following':following['following_data'],
                             'likedposts':likedposts,'userposts':userposts}
            return response
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response
    
class UserByNameView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            if request.data['username'] == payload['username']:
                username = payload['username']
                user = getuserfunc(username)
                followers = getfollowersfunc(username)
                following = getfollowingfunc(username)
                userposts = getuserpostsfunc(username)
                response.status_code = 200
                response.data = {'userstatus':1,'user':user,'followers':followers['follower_data'],'following':following['following_data'],'userposts':userposts}
                return response
            
            username = request.data['username']
            user = getuserfunc(username)
            followers = getfollowersfunc(username)
            following = getfollowingfunc(username)
            userposts = getuserpostsfunc(username)
            liked_posts = getlikedpostsfunc(payload['username'])
            response.status_code = 200
            response.data = {'userstatus':0,'user':user,'followers':followers['follower_data'],'following':following['following_data'],'userposts':userposts,'likedposts':liked_posts}
            return response
        
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response

class FollowersView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = request.data['username']
            followers = getfollowersfunc(username)
            follower_count = len(followers['follower_data'])
            ownedProfile = 0
            if username == payload['username']:
                ownedProfile = 1
            response.status_code = 200
            response.data = {'ownedProfile':ownedProfile,'followers':followers['follower_data'],'follower_count':follower_count}
            return response
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response
    
class FollowingView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = request.data['username']
            following = getfollowingfunc(username)
            following_count = len(following['following_data'])
            ownedProfile = 0
            if username == payload['username']:
                ownedProfile = 1
            response.status_code = 200
            response.data = {'ownedProfile':ownedProfile,'following':following['following_data'],'following_count':following_count}
            return response
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response
    
class RegisterView(APIView):
    def post(self, request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        if Profile.objects.filter(username__exact=request.data['username']).first() is not None:
            response.status_code = 422
            response.data = {'Problem':'username','Message':'Username already taken'}
            return response

        if Profile.objects.filter(email__exact=request.data['email']).first() is not None:
            response.status_code = 422
            response.data = {'Problem':'email','Message':'Mail already taken'}
            return response
        try:
            serializer = ProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response.data = serializer.data
            response.status_code= 201
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
        return response

class LoginView(APIView):
    def post(self, request):
        response = Response()
        # Check brute force attack
        IP = request.data['IP']
        blockedIP = BlockedIP.objects.filter(username=request.data['username'],IP=IP).first()
        if blockedIP is not None:
            current_time = timezone.now()
            time_difference = current_time - blockedIP.timestamp
            if time_difference >= timedelta(minutes=15):
                blockedIP.delete()
                counter = IP_count.objects.filter(IP=IP).first()
                counter.delete()
            else:
                response.status_code = 401
                response.data = {'Problem':'Brute Force','Message':'Too many attemps try again later!'}
                return response

        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        password = request.data['password']
        username = request.data['username']
        profile = Profile.objects.filter(username__exact=username).first()

        # try:
        #     mail = request.data['email']
        #     profile = Profile.objects.filter(email__exact=mail).first()

        # except:
        #     username = request.data['username']
        #     profile = Profile.objects.filter(username__exact=username).first()

        if profile is None:
            response.status_code = 404
            response.data = {'Problem':'user','Message':'User not found'}
            return response
        
        if not profile.check_password(password):
            response.status_code = 401
            response.data = {'Problem':'password','Message':'Wrong password'}

            counter = IP_count.objects.filter(username=request.data['username'],IP=IP).first()
            if counter is None:
                new_counter = IP_count.objects.create(username=request.data['username'],IP=IP)
                new_counter.save()
            else:
                current_time = timezone.now()
                time_difference = current_time - counter.timestamp
                if time_difference >= timedelta(minutes=10):
                    counter.delete()
                    new_counter = IP_count.objects.create(username=request.data['username'],IP=IP)
                    new_counter.save()
                else:
                    counter.count += 1
                    counter.save()
                    if counter.count >= 10:
                        new_blockedIP = BlockedIP.objects.create(username=request.data['username'],IP=IP)
                        new_blockedIP.save()
                        response.status_code = 401
                        response.data = {'Problem':'Brute Force','Message':'Too many attemps, please wait 15 minutes before trying!'}
            return response
        # seralized_data = ProfileSerializer(profile)

        counter_check = IP_count.objects.filter(username=request.data['username'],IP=IP).first()
        if counter_check is not None:
            counter_check.delete()
        payload = {
            'username':username,
            'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()
        }
        token = jwt.encode(payload,decode_key, algorithm='HS256')
        response.status_code = 302
        response.set_cookie(key='jwt',value=token,httponly=True)
        return response

class UserView(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        try:
            profile = Profile.objects.filter(username__exact=payload['username']).first()
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
            print(str(e))
        return response

class LogoutView(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        try:
            response.status_code = 200
            response.delete_cookie('jwt')
            response.data = {'Message':'Success'}
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
        return response
    
class DeleteUserView(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        try:
            profile = Profile.objects.filter(id=payload['id']).first()
            profile.delete()
            response.status_code = 200
            response.delete_cookie('jwt')
            response.data = {'Message':'Success'}
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message': str(e)}
        return response

class UploadPost(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            if payload['username'] == request.data['username']:
                new_post = Post.objects.create(userID = request.data['id'],app_id=request.data['app_id'],game_name=request.data['game_name'],teammates=request.data['teammates'],tags=request.data['tags'],username=request.data['username'],url=request.data['url'],caption=request.data['caption'],profile_image=request.data['profile_image'])
                new_post.save()
                response.status_code = 200
                return response
            else:
                response.status_code = 401
                response.data = {'Problem':'authentication','Message':'Not authorized'}
                return response

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetPosts(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            
            following = Follower.objects.filter(follower__exact=payload['username'])
            following = FollowerSerializer(following,many=True).data
            
            following_list = [payload['username']]
            for i in following:
                following_list.append(i['username'])
                
            posts = Post.objects.filter(username__in=following_list).order_by('created_at')
            serializer = PostSerializer(posts,many=True)
            return Response(serializer.data)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetLikedPosts(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            post_objects = Post_like.objects.filter(username__exact=payload['username'])
            posts = LikeSerializer(post_objects,many=True)
            liked_posts = []
            for post in posts.data:
                liked_posts.append(post['postID'])
            response.data = liked_posts
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
                    
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
            print(str(e))
        return response
    
class LikePost(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            like_check = Post_like.objects.filter(username__exact = payload['username'],postID=request.data['postID']).first()
            post = Post.objects.filter(postID = request.data['postID']).first()
            if like_check is None:
                post.number_of_likes += 1
                post.save()
                new_like = Post_like.objects.create(username = payload['username'],postID=request.data['postID'])
                new_like.save()
                response.data = {'liked':1,'number_of_likes':post.number_of_likes}
            else:
                post.number_of_likes -= 1 
                post.save() 
                like_check.delete()
                response.data = {'liked':0,'number_of_likes':post.number_of_likes}
            response.status_code = 200
            return response

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetPostLikes(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            postID = request.data['postID']
            likes_data = Post_like.objects.filter(postID=postID)
            likes = LikeSerializer(likes_data,many=True).data
            liked_profiles = []
            
            for like in likes:
                liked_profiles.append(like['username'])
            profiles_data = Profile.objects.filter(username__in=liked_profiles)
            profiles = ProfileSerializer(profiles_data,many=True)
            return Response(profiles.data)
                
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
                    
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response
    
class ChangeProfilePicture(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            if payload['username'] == request.data['username']:
                user = Profile.objects.get(username__exact=payload['username'])
                user.profile_image = request.data['profile_image']
                user.save()
                posts = Post.objects.filter(username__exact=payload['username'])
                for post in posts:
                    post.profile_image = request.data['profile_image']
                    post.save()
                response.status_code = 200
                
            else:
                response.status_code = 401
                response.data = {'Problem':'authentication','Message':'Not authorized'}
                
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
                    
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response
    
class DeletePost(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            post = Post.objects.get(postID = request.data['postID'])
            if payload['username'] == post.username:
                post.delete()
                response.status_code = 200
            else:
                response.status_code = 401
                response.data = {'Problem':'authentication','Message':'Not authorized'}

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response

class Follow(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = payload['username']
            following = request.data['follow_username']

            user = Profile.objects.get(username__exact=username)
            follow_user = Profile.objects.get(username__exact=following)
            isFollowing = Follower.objects.filter(username__exact=follow_user,follower=username).first()
            if isFollowing:
                response.status_code = 401
                response.data = {'Problem':'Following','Message':'Already following this user'}
                return response
            
            if user is not None and follow_user is not None:
                follower = Follower.objects.create(username=following, follower=username)
                follower.save()

                response.status_code = 200
            else:
                response.status_code = 404
                response.data = {'Problem':'follow_user','Message':'User does not exists'}

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetFollowers(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            username = request.data['username']
            
            followers = Follower.objects.filter(username__exact=username)
            serializer = FollowerSerializer(followers,many=True).data
            
            follower_list = []
            for i in serializer:
                follower_list.append(i['follower'])
                
            users = Profile.objects.filter(username__in=follower_list)
            users = FilteredProfileSerializer(users,many=True)
            return Response(users.data)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetFollowing(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            username =  request.data['username']
            following = Follower.objects.filter(follower__exact=username)
            following = FollowerSerializer(following,many=True).data
            
            following_list = []
            for i in following:
                following_list.append(i['username'])
                
            users = Profile.objects.filter(username__in=following_list)
            users = FilteredProfileSerializer(users,many=True)
            return Response(users.data)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response
    
class Unfollow(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            user = payload['username']
            follow = Follower.objects.filter(username__exact=request.data['unfollow_username'],follower=user)
            follow.delete()
            response.status_code = 200

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response
    
class GetUsers(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            users = Profile.objects.all()
            serializer = ProfileSerializer(users,many=True)
            return Response(serializer.data)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response   
    
class GetFollowSuggestion(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            username = payload['username']
            
            following = Follower.objects.filter(follower__exact=payload['username'])
            following = FollowerSerializer(following,many=True).data
            
            following_list = [username]
            for i in following:
                following_list.append(i['username'])

            users = Profile.objects.filter().exclude(username__in=following_list)
            users = ProfileSerializer(users,many=True).data
            return Response(users)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
        return response  

class GetUSerPosts(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            posts = Post.objects.filter(username__exact=request.data['username']).order_by('created_at')
            serializer = PostSerializer(posts,many=True)
            return Response(serializer.data)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            response.data = {'Problem':'server','Message':str(e)}
            print(str(e))
        return response

class SteamID(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            user = Profile.objects.filter(steamid=request.data['steamid']).first()
            if user is not None:
                response.status_code = 405
                response.data = {'Message':'Steam profile already connected to another account!'}
                return response
            steamconnection = ConnectSteamProfile({'steamid':request.data['steamid'],'username':payload['username']})
            libraryUpdate = UpdateLibrary({'steamid':request.data['steamid'],'username':payload['username']})
            if steamconnection['Problem'] is not None:
                response.status_code = 500
                response.data['Problem':'Steam','Message':steamconnection['Message']]
            elif libraryUpdate['Problem'] is not None:
                response.status_code = 500
                response.data['Problem':'Steam','Message':steamconnection['Message']]

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response
    
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            user = Profile.objects.filter(steamid=request.data['steamid']).first()
            if user is None:
                response.data = {'usersearch':0}
            else:
                response.data = {'usersearch':1}

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GameList(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            game_objects = Game.objects.all()
            games = GameSerializer(game_objects,many=True)
            return Response(games.data)
        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetProfile(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            user = Profile.objects.filter(username__exact=request.data['username']).first()
            if user is not None:
                serializer = FilteredProfileSerializer(user)
                response.status_code = 200
                return Response(serializer.data)
            response.status_code = 404
            response.data = {'Problem':'user','Message':'User does not exist'}

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response        

class UpdateUser(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            user = Profile.objects.filter(username__exact=payload['username']).first()
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.about = request.data['about']
            user.save()

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response  

class Comment(APIView):
    def post(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            payload = jwt.decode(token,decode_key,algorithms=['HS256'])
            new_comment = Post_Comment.objects.create(username=payload['username'],comment=request.data['comment'],postID=request.data['postID'])
            new_comment.save()
            post = Post.objects.filter(postID=request.data['postID']).first()
            post.latest_comment = request.data['comment']
            post.latest_comment_username = payload['username']
            post.save()
            response.status_code = 200
            response.data = {'username':payload['username']}
            return response

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response

class GetComments(APIView):
    def get(self,request):
        response = Response()
        if request.data['API_KEY'] not in API_KEYS:
            response.status_code = 401
            response.data = {'Problem':'API_KEY','Message':'API Key not valid'}
            return response
        token = request.COOKIES.get('jwt')
        if not token:
            response.status_code = 401
            response.data = {'Problem':'authentication','Message':'Not authenticated'}
            return response
        try:
            comments_objects = Post_Comment.objects.filter(postID=request.data['postID'])
            comments = CommentSerializer(comments_objects,many=True).data
            return Response(comments)

        except jwt.ExpiredSignatureError:
            response.status_code = 401
            response.data = {'Problem':'expired','Message':'Authentication expired'}
            return response
        
        except Exception as e:
            response.status_code = 500
            print(str(e))
            response.data = {'Problem':'server','Message':str(e)}
        return response