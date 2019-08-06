from django.urls import path
from django.contrib.auth.decorators import login_required
from account import views

# namespace
app_name = 'account'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register_interests/', views.RegisterInterestsView.as_view(), name='register_interests')
    # path('search/',views.SearchView.as_view(), name='search'),

    # # login required
    # path('collect/',views.CollectView.as_view(), name='collect'),
    # path('feeds/', views.FeedsView.as_view(),name='feeds'),
    # path('click/',views.ClickView.as_view(), name='click'),
    # # path('profile/',views.ProfileView.as_view(), name='profile'),
    # path('trending/',views.TrendingView.as_view(), name='trending'),
    # path('subscribe/',views.SubscribeView.as_view(), name='subscribe')
    
    
]
