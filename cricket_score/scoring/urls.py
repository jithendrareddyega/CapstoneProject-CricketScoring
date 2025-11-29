from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Web views
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create-match/', views.create_match, name='create_match'),
    path('match/<int:match_id>/', views.match_dashboard, name='match_dashboard'),
    path('match/<int:match_id>/add-players/', views.add_players, name='add_players'),

    # API
    path('api/get-token/', api_views.get_token, name='api_get_token'),
    path('api/matches/', api_views.match_list_create, name='api_match_list_create'),
    path('api/matches/<int:pk>/', api_views.match_detail, name='api_match_detail'),
]
