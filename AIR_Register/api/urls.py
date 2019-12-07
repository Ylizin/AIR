from django.urls import path
from django.contrib.auth.decorators import login_required
from api import views

# namespace
app_name = 'api'
urlpatterns = [
    path('search/',views.SearchView.as_view(), name='search'),
    # login required
    path('collect/',views.CollectView.as_view(), name='collect'),
    path('feeds/', views.FeedsView.as_view(),name='feeds'),
    path('click/',views.ClickView.as_view(), name='click'),
    # path('profile/',views.ProfileView.as_view(), name='profile'),
    path('trending/',views.TrendingView.as_view(), name='trending'),
    path('subscribe/',views.SubscribeView.as_view(), name='subscribe'),
    path('tab/',views.TabView.as_view(), name='tab')
    
]
