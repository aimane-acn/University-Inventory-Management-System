from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name="signup"),
    path('signup/', views.signup, name="signup_slash"),
    path('', views.my_login, name="my_login"), 
    path('home', views.home, name="home"),
    path('logout', views.Logout, name='logout'),
]
