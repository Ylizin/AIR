from django.urls import path

from . import views

app_name = 'online'
urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
]