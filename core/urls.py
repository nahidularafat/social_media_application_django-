from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Homepage
    path('settings', views.settings, name='settings'), # Settings page
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
     path('search', views.search, name='search'),
    path('profile/<str:pk>',views.profile,name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),  # Signup page
    path('signin', views.signin, name='signin'),  # Signin page
    path('logout', views.logout, name='logout'),  # Logout page
    
]
