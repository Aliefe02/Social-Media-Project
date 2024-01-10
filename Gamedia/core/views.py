from django.shortcuts import render, redirect
from django.http import HttpResponse,Http404, JsonResponse
import requests
from django.contrib import messages
import cloudinary
import cloudinary.uploader
import cloudinary.api
import datetime
import json
from steamauth import auth, get_uid
from ipware import get_client_ip


cloudinary.config(
  cloud_name="dh3oyo4uz",
  api_key="693741296779315",
  api_secret="Lxfe0JCfeWp3xm55o3r7IR855yU"
  )

API_KEY = 'Gamedia_first_api_key'

API_URL = 'http://localhost:8000/api/'

def signup(request):
    if request.method == 'POST':
        try:
            client_ip, is_routable = get_client_ip(request)
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password']
            url = API_URL+"register"
            data = {'username': username, 'email': email, 'password': password , 'API_KEY':API_KEY,'IP':client_ip}
            r = requests.post(url, json=data)
            if r.status_code == 201:
                return redirect('signin')
            try:
                error_message = r.json()['Message']
            except:
                error_message = ''
            messages.info(request,error_message)
            return redirect('signup')
        except:
            raise Http404()
    if request.COOKIES.get('jwt') is not None:
        return redirect('/')
    return render(request, 'signup.html')

def index(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}

    r = requests.get(API_URL+'indexView',cookies=cookie,data={'API_KEY':API_KEY})
    data = r.json()
    if r.status_code == 401:
        if data['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif r.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    elif r.status_code == 200:       
        following_count = len(data['following'])
        response = render(request, 'index.html',{'posts':data['posts'], "user":data['user'], "users":data['followsuggestion'], 
                                                 "following":data['following'],"following_count":following_count,'liked_posts':data['likedposts']})
        response.set_cookie(key='jwt', value=token, httponly=True)      
        return response
        
    return Http404()

def UserByName(request,username):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}

    r = requests.get(API_URL+'userbynameView',cookies=cookie,data={'API_KEY':API_KEY,'username':username})
    data = r.json()
    if r.status_code == 401:
        if data['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif r.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    elif r.status_code == 200:  
        if data['userstatus'] == 1:
            return redirect('Profile')
             
        following_count = len(data['following'])
        follower_count = len(data['followers'])
        post_count = len(data['userposts'])
        response = render(request, 'userbyname.html',{'post_count':post_count,'posts':data['userposts'], "profile":data['user'],
                                     "following":data['following'],"following_count":following_count,'follower_count':follower_count,
                                     'followers':data['followers'],'liked_posts':data['likedposts']})
        response.set_cookie(key='jwt', value=token, httponly=True)      
        return response

def signin(request):
    if request.method == 'POST':
        # if '@' in request.POST['username']:
        #     email = request.POST['username']
        #     password = request.POST['password']
        #     data = {'email':email,'password':password,'API_KEY':API_KEY}
        # else:
        client_ip, is_routable = get_client_ip(request)
        username = request.POST['username']
        password = request.POST['password']
        data = {'username':username,'password':password,'API_KEY':API_KEY,'IP':client_ip}

        url = API_URL+"login"
        r = requests.post(url,json=data)

        if r.status_code == 302:
            token = r.cookies['jwt']
            response = redirect('index')
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.status_code = 302
            return response
        elif r.status_code == 500:
            messages.info(request,'Retry please')
            return redirect('signin')
        elif r.status_code == 401 or r.status_code == 404:
            messages.info(request,r.json()['Message'])
            return redirect('signin')
        else:
            raise Http404()
    if request.COOKIES.get('jwt') is not None:
        return redirect('/')
    return render(request,'signin.html')

def Settings(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}
    user_data = requests.get(API_URL+'user',cookies=cookie,data={'API_KEY':API_KEY})
    user = user_data.json()

    if user_data.status_code == 401:
        if user['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif user_data.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    if user_data.status_code == 200:
        try:
            if request.method == 'POST':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                about = request.POST['about']
                requests.post(API_URL+'updateuser',cookies=cookie,data={'API_KEY':API_KEY,'first_name':first_name,'last_name':last_name,'about':about})
                return redirect('settings')
            else:
                response = render(request, 'settings.html',{"user":user})
                response.set_cookie(key='jwt', value=token, httponly=True)      
                return response
        except Exception as e:
            print(str(e))
    return redirect('/')

def logout(request):
    response = redirect('signin')
    response.delete_cookie('jwt')
    return response

def uploadPost(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}
    r = requests.get(API_URL+'user',cookies=cookie,data={'API_KEY':API_KEY})
    data = r.json()
    
    if r.status_code == 401:
        if data['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif r.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    if request.method == 'POST':
        try:
            caption = request.POST['caption']
            id = data['id']
            username = data['username']
            cloudinary_response = cloudinary.uploader.upload(request.FILES['image_upload'])
            image_url = cloudinary_response['url']
            game_details = request.POST['Game']
            if game_details != '':
                game_id = game_details.split('?', 1)[0]
                game_name = game_details.split('?', 1)[1]
            else:
                game_id = ''
                game_name = ''
            data = {'id':id,'username':username,'url':image_url,'caption':caption,'profile_image':data['profile_image'],'API_KEY':API_KEY,'app_id':game_id, 'game_name':game_name,'teammates':request.POST['teammates'],'tags':request.POST['tags']}
            requests.post(API_URL+'uploadpost',cookies=cookie,data=data)
            return redirect('index')
        except Exception as e:
            print(str(e))
    games = requests.get(API_URL+'gamelist',cookies=cookie,data={'API_KEY':API_KEY}).json()
    response = render(request,'uploadpost.html',{'user':data,'games':games})
    return response

def DeletePost(request):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            postID = request.GET['postID']
            data={"postID":postID,'API_KEY':API_KEY}
            r = requests.post(API_URL+'deletepost',cookies=cookie,data=data)
            status_code = r.status_code
        except Exception as e:
            status_code = 500
            print(str(e))

        if status_code == 401:
            if data['Problem'] == 'expired':
                messages.info(request,'Login Expired')
                return redirect('signin')
            messages.info(request,'Not Authenticated')
            return redirect('signin')
        
        # ---------------- ADD EXCEPTION FOR status_code = 500 ------------------------
    return redirect('/')

def Follow(request):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            data={"follow_username":request.GET['followuser'],'API_KEY':API_KEY}
            r = requests.post(API_URL+'follow',cookies=cookie,data=data)
            status_code = r.status_code
        except Exception as e:
            status_code = 500
            print(str(e))
        if status_code == 401:
            if data['Problem'] == 'expired':
                messages.info(request,'Login Expired')
                return redirect('signin')
            messages.info(request,'Not Authenticated')
            return redirect('signin')
        
        # ---------------- ADD EXCEPTION FOR status_code = 500 ------------------------
    return redirect('/')

def Unfollow(request):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            data={"unfollow_username":request.GET['unfollowuser'],'API_KEY':API_KEY}
            r = requests.post(API_URL+'unfollow',cookies=cookie,data=data)
            status_code = r.status_code
        except Exception as e:
            status_code = 500
            print(str(e))
        if status_code == 401:
            if data['Problem'] == 'expired':
                messages.info(request,'Login Expired')
                return redirect('signin')
            messages.info(request,'Not Authenticated')
            return redirect('signin')
        
        # ---------------- ADD EXCEPTION FOR status_code = 500 ------------------------
    return redirect('/')

def Profile(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}

    r = requests.get(API_URL+'profileView',cookies=cookie,data={'API_KEY':API_KEY})
    data = r.json()
    if r.status_code == 401:
        if data['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif r.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    elif r.status_code == 200:       
        following_count = len(data['following'])
        follower_count = len(data['followers'])
        post_count = len(data['userposts'])
        response = render(request, 'profile.html',{'post_count':post_count,'posts':data['userposts'], "user":data['user'],
                                     "following":data['following'],"following_count":following_count,'follower_count':follower_count,
                                     'followers':data['followers'],'liked_posts':data['likedposts']})
        response.set_cookie(key='jwt', value=token, httponly=True)      
        return response
        
    return redirect('/')

def LikePost(request):
    if request.method == 'POST':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            postID = request.POST.get("postID")
            like = requests.post(API_URL+'likepost',cookies=cookie,data={'API_KEY':API_KEY,'postID':postID})
            if like.status_code == 401:
                if like.json()['Problem'] == 'expired':
                    messages.info(request,'Login Expired')
                    return redirect('signin')
                messages.info(request,'Not Authenticated')
                return redirect('signin')
            
            elif like.status_code == 500:
                messages.info(request,'Try Again')
                return redirect('signin')
            like_status = like.json()
            return JsonResponse({'status':like_status['liked'],'number_of_likes':str(like_status['number_of_likes'])},safe=False)
        except Exception as e:
            print(str(e))
    return redirect('/')

def connectionResult(request):
    return render(request,'connectionResult.html')

def login(request):
    return auth('/callback', use_ssl=False)


def login_callback(request):
    steam_uid = get_uid(request.GET)
    if steam_uid is None:
        messages.info(request,'There was a problem connecting your account to Steam, try again!')
        return redirect('connectionResult')
    else:
        token = request.COOKIES.get('jwt')
        cookie = {'jwt':token}  
        r = requests.post(API_URL+'steamid',cookies=cookie,data={'API_KEY':API_KEY,'steamid':int(steam_uid)})
        if r.status_code == 405:
            messages.info(request,'This Steam Account is Already Connected to Another Account!')
        elif r.status_code:
            messages.info(request,'Steam Account Connected Succesfully!')
        return redirect('connectionResult')

def PostLikes(request):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            postID = request.GET['postID']
            like = requests.get(API_URL+'getpostlikes',cookies=cookie,data={'API_KEY':API_KEY,'postID':postID})
            if like.status_code == 401:
                if like.json()['Problem'] == 'expired':
                    messages.info(request,'Login Expired')
                    return redirect('signin')
                messages.info(request,'Not Authenticated')
                return redirect('signin')
            
            elif like.status_code == 500:
                messages.info(request,'Try Again')
                return redirect('signin')
            
            liked_profiles = like.json()
            like_count = len(liked_profiles)

            return render(request,'userlist.html',{'message':'Likes','profiles':liked_profiles,'count':like_count})
        except Exception as e:
            print(str(e))
    return redirect('/')

def Followers(request,username):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        r = requests.get(API_URL+'followersView',cookies=cookie, data={'API_KEY':API_KEY,'username':username})
        data = r.json()
        if r.status_code == 401:
            if data['Problem'] == 'expired':
                messages.info(request,'Login Expired')
                return redirect('signin')
            messages.info(request,'Not Authenticated')
            return redirect('signin')
        
        elif r.status_code == 500:
            messages.info(request,'Try Again')
            return redirect('signin')
        
        elif r.status_code == 200:
            try:
                response = render(request, 'userlist.html',{'message':'Followers',"profiles":data['followers'],'count':data['follower_count'],'ownedProfile':data['ownedProfile']})
                response.set_cookie(key='jwt', value=token, httponly=True)   
                return response
            except Exception as e:
                print(str(e))
    return redirect('/')

def Following(request,username):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        r = requests.get(API_URL+'followingView',cookies=cookie, data={'API_KEY':API_KEY,'username':username})
        data = r.json()
        if r.status_code == 401:
            if data['Problem'] == 'expired':
                messages.info(request,'Login Expired')
                return redirect('signin')
            messages.info(request,'Not Authenticated')
            return redirect('signin')
        
        elif r.status_code == 500:
            messages.info(request,'Try Again')
            return redirect('signin')
        
        elif r.status_code == 200:
            try:
                response = render(request,'userlist.html',{'message':'Following',"profiles":data['following'],'count':data['following_count'],'ownedProfile':data['ownedProfile']})
                response.set_cookie(key='jwt', value=token, httponly=True)   
                return response
            except Exception as e:
                print(str(e))
    return redirect('/')

def ChangeProfilePicture(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return redirect('signin')
    cookie = {'jwt':token}
    r = requests.get(API_URL+'user',cookies=cookie,data={'API_KEY':API_KEY})
    data = r.json()
    
    if r.status_code == 401:
        if data['Problem'] == 'expired':
            messages.info(request,'Login Expired')
            return redirect('signin')
        messages.info(request,'Not Authenticated')
        return redirect('signin')
    
    elif r.status_code == 500:
        messages.info(request,'Try Again')
        return redirect('signin')
    
    if request.method == 'POST':
        try:
            username = data['username']
            cloudinary_response = cloudinary.uploader.upload(request.FILES['image_upload'])
            image_url = cloudinary_response['url']
            data = {"username":username,"profile_image":image_url,'API_KEY':API_KEY}
            requests.post(API_URL+'changeprofilepicture',cookies=cookie,data=data)
            return redirect('/')
        
        except Exception as e:
            print(str(e))
    response = render(request,'profilepicture.html',{'user':data})
    return response

def Comment(request):
    if request.method == 'POST':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            postID = request.POST.get("postID")
            new_comment = requests.post(API_URL+'comment',cookies=cookie,data={'API_KEY':API_KEY,'postID':postID,'comment':request.POST.get("comment")})
            if new_comment.status_code == 401:
                if new_comment.json()['Problem'] == 'expired':
                    messages.info(request,'Login Expired')
                    return redirect('signin')
                messages.info(request,'Not Authenticated')
                return redirect('signin')
            
            elif new_comment.status_code == 500:
                messages.info(request,'Try Again')
                return redirect('signin')
            return JsonResponse({'status':1,'username':new_comment.json()['username']},safe=False)
        except Exception as e:
            print(str(e))
    return redirect('/')

def CommentList(request):
    if request.method == 'GET':
        token = request.COOKIES.get('jwt')
        if not token:
            return redirect('signin')
        cookie = {'jwt':token}
        try:
            postID = request.GET['postID']
            comments = requests.get(API_URL+'getcomments',cookies=cookie,data={'API_KEY':API_KEY,'postID':postID})
            if comments.status_code == 401:
                if comments.json()['Problem'] == 'expired':
                    messages.info(request,'Login Expired')
                    return redirect('signin')
                messages.info(request,'Not Authenticated')
                return redirect('signin')
            
            elif comments.status_code == 500:
                messages.info(request,'Try Again')
                return redirect('signin')
            
            comments = comments.json()
        
            return render(request,'comments.html',{'comments':comments})
        except Exception as e:
            print(str(e))
    return redirect('/')