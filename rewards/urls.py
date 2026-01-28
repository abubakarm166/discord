from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('auth/discord/login/', views.discord_oauth_login, name='discord_login'),
    path('auth/discord/callback/', views.discord_oauth_callback, name='discord_callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('api/redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
]
