from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("callback/", views.callback, name="auth_callback"),
    path("logout/", views.logout, name="logout"),
]
