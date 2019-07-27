from django.urls import path

from account import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='register'),
    path('register/', views.RegisterView.as_view(), name='register'),
    # path('detail/', views.user_detail),
]