from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("token/refresh/", views.token_refresh, name="token_refresh"),
    path("login/", views.login, name="login"),
    path("callback/", views.callback, name="auth_callback"),
    path("logout/", views.logout, name="logout"),
]
