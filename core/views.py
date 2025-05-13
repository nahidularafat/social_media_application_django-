from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib import messages, auth
from django.http import HttpResponse, JsonResponse
from itertools import chain
import random

@login_required(login_url='signin')
def index(request):
    # বর্তমান ইউজার এবং প্রোফাইল
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # যাদেরকে ইউজার ফলো করে
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    user_following_list = [u.user for u in user_following]

    # ফলো করা ইউজারদের পোস্ট
    feed = [Post.objects.filter(user=username) for username in user_following_list]

    # ✅ নিজের পোস্ট
    user_posts = Post.objects.filter(user=request.user)

    # ✅ নিজের পোস্ট + ফলো করা ইউজারদের পোস্ট
    feed_list = list(chain(user_posts, *feed))

    # ইউজার সাজেশন
    all_users = User.objects.all()

    # ফলো করা ইউজারদের ইউজার অবজেক্ট সংগ্রহ
    user_following_all = User.objects.filter(username__in=user_following_list)

    # নিজে এবং ফলো করা ছাড়া বাকি সবাই
    current_user = request.user
    new_suggestions_list = [
        user for user in all_users
        if user not in user_following_all and user != current_user
    ]

    # র‍্যান্ডম সাজেশন
    random.shuffle(new_suggestions_list)

    # সাজেশন ইউজারদের প্রোফাইল
    username_profile_list = []
    for user in new_suggestions_list[:10]:  # একটু বেশি নিয়ে পরে [:4] দেখাচ্ছি
        profiles = Profile.objects.filter(user=user)
        username_profile_list.append(profiles)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(
        request,
        'index.html',
        {
            'user_profile': user_profile,
            'posts': feed_list,
            'suggestions_username_profile_list': suggestions_username_profile_list[:4]  # শুধু ৪টা দেখানো হবে
        }
    )



@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption', '')

        if image:
            Post.objects.create(user=user, image=image, caption=caption)
        return redirect('/')

    return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    username_profile_list = []

    if request.method == 'POST':
        username = request.POST['username']
        username_objects = User.objects.filter(username__icontains=username)

        # User ID নিয়ে Profile বের করা
        for user in username_objects:
            profiles = Profile.objects.filter(user=user)
            username_profile_list.append(profiles)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {
        'user_profile': user_profile,
        'username_profile_list': username_profile_list  # spelling fixed
    })
    
@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter is None:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
    else:
        like_filter.delete()
        post.no_of_likes -= 1

    post.save()

    # লাইক সংখ্যা অনুযায়ী টেক্সট তৈরি করো
    if post.no_of_likes == 0:
        likes_text = "No likes"
    elif post.no_of_likes == 1:
        likes_text = "Liked by 1 person"
    else:
        likes_text = f"Liked by {post.no_of_likes} people"

    return JsonResponse({'likes_text': likes_text})
    
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)  # Fetch user by username
    user_profile = Profile.objects.get(user=user_object)  # Fetch user profile
    user_posts = Post.objects.filter(user=pk)  # Fetch all posts by that user
    user_post_length = len(user_posts)  # Count the posts

    follower = request.user.username
    user = pk

    # Check if the user is already following
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"    

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }

    return render(request, 'profile.html', context)  # Pass the context to profile.html
       
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        else:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):  
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']  # Ensure form uses name="password"
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)
                # Create user profile
                new_profile = Profile.objects.create(user=user, id_user=user.id)
                new_profile.save()

                messages.success(request, 'Account created successfully!')
                return redirect('settings')  # Or wherever you want after signup
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        # যদি ইতোমধ্যে follower এবং user এর মাঝে follow relationship থাকে
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)

        # না থাকলে নতুন follow relationship তৈরি করো
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)

    else:
        return redirect('/')