from django.urls import path
from django.contrib.auth.decorators import login_required
from account import views

# namespace
app_name = 'account'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register_interests/', views.RegisterInterestsView.as_view(), name='register_interests'),
    path('collect/', views.CollectView.as_view(), name='collect'),

    path('register_success/', views.IndexView.as_view(), name='register_success'),
    path('feeds/', views.FeedsView.as_view(),name='feeds'),
    path('index/',login_required(views.IndexView.as_view()), name='index')
    
]
