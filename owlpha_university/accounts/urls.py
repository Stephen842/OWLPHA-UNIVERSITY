from django.urls import path
from . import views
from django.contrib.auth import views as auth


urlpatterns = [
    path('', views.home, name='home'),
    path('testing', views.testing, name='testing'),
    
    # Sign Up, Sign in, Sign Out and Password reset routes
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('password-reset/', auth.PasswordResetView.as_view(template_name = 'pages/password_reset.html'), name = 'password_reset'),
    path('password-reset/', auth.PasswordResetView.as_view(template_name = 'pages/password_reset_email.html'), name = 'password_reset'),
    path('password-reset/done/', auth.PasswordResetDoneView.as_view(template_name = 'pages/password_reset_done.html'), name = 'password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(template_name='pages/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/', auth.PasswordResetCompleteView.as_view(template_name = 'pages/password_reset_complete.html'), name = 'password_reset_complete'),

    # Account verification and activation
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('resend-activation/<uidb64>/', views.resend_activation_email, name='resend_activation_email'), 
]