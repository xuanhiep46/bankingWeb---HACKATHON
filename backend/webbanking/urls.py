from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('api/login/', views.apiLogin, name='apiLogin'),
    path('api/signup/', views.apiSignup, name='apiSignup'),
    path('verify/', views.verify, name='verify'),
    path('api/verify/', views.apiVerify, name='apiVerify'),
    path('interface/', views.interface, name='interface'),

]
