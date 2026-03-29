from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name ='feed'),
    path('profile/', views.profile, name ='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('discover/', views.discover, name='discover'),
    path('create-group/', views.create_group, name='create_group'),
]


