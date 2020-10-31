from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Like, Post, User, UserFollowing


def index(request):
    posts = Post.objects.order_by('-time_posted')
    if request.user.is_authenticated:
        annotated_posts = [{"id": post.id, "content": post.content, "time_posted": post.time_posted,
                    "user": post.user, "likes": post.likes, "liked": post.user_like(request.user)} for post in posts]
    else:
        annotated_posts = [{"id": post.id, "content": post.content, "time_posted": post.time_posted,
                            "user": post.user, "likes": post.likes, "liked": False} for post in posts]
    paginator = Paginator(annotated_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {'page_obj': page_obj})

    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    content = data.get("content", "")
    post = Post(content=content, user=request.user)
    post.save()
    return JsonResponse(post.serialize(), safe=False)

def profile(request, id):
    user = User.objects.get(id=id)
    posts = user.posts.order_by('-time_posted')
    annotated_posts = [{"id": post.id, "content": post.content, "time_posted": post.time_posted,
                    "user": post.user, "likes": post.likes, "liked": post.user_like(request.user)} for post in posts]
    paginator = Paginator(annotated_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    is_following = True if request.user.following.filter(following_user_id=id) else False
    following = user.following.count()
    followers = user.followers.count()
    return render(request, "network/profile.html", {'page_obj': page_obj, 
         'profile': user,'following': following, 'followers': followers,
         'is_following': is_following})

@csrf_exempt
@login_required
def follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    following = int(data.get("user"))
    try:
        follow_obj = UserFollowing.objects.get(user_id=User.objects.get(id=request.user.id),
                                        following_user_id=User.objects.get(id=following))
        follow_obj.delete()
        icon = "yes"
    except UserFollowing.DoesNotExist:
        UserFollowing.objects.create(user_id=User.objects.get(id=request.user.id),
                                 following_user_id=User.objects.get(id=following))
        icon = "no"                                
    user_ = User.objects.get(id=following)
    followers = user_.followers.count()
    return JsonResponse({"followers": followers, "icon": icon}, safe=False)

@login_required
def following(request):
    followed_people = UserFollowing.objects.filter(user_id=request.user).values('following_user_id')
    posts = Post.objects.filter(user__in=followed_people).order_by('-time_posted')
    annotated_posts = [{"id": post.id, "content": post.content, "time_posted": post.time_posted,
                    "user": post.user, "likes": post.likes, "liked": post.user_like(request.user)} for post in posts]
    paginator = Paginator(annotated_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {'page_obj': page_obj})

@csrf_exempt
@login_required
def like(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post = int(data.get("post"))
    like_obj = Like.objects.filter(likes=User.objects.get(id=request.user.id),
                                   liked_by=Post.objects.get(id=post))
    post_ = Post.objects.get(id=post)
    if like_obj:
        like_obj.delete()
        post_.likes -= 1
        post_.save()
        icon = "yes"
    else:                                
        Like.objects.create(likes=User.objects.get(id=request.user.id),
                        liked_by=Post.objects.get(id=post))
        post_.likes += 1
        post_.save()
        icon = "no"
    return JsonResponse({"likes": post_.likes, "icon": icon}, safe=False)


@csrf_exempt
@login_required
def edit(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post_id = int(data.get("id")[1:])
    content = data.get("content")
    post = Post.objects.get(id=post_id)
    post.content = content
    post.save()
    return JsonResponse(post.serialize(), safe=False)