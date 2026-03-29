from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('login/', views.login, name='login'),
    path('profile/', views.user_profile, name='user-profile'),
    path('password-reset/request/', views.request_password_reset, name='password-reset-request'),
    path('password-reset/confirm/', views.reset_password_confirm, name='password-reset-confirm'),
    path('change-password/', views.change_password, name='change-password'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),
]