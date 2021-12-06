from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("userhome", views.userpage, name="userpage"),
    path("register", views.register_request, name="register"),
    path("logout", views.logout_request, name="logout"),
    path("login", views.login_request, name="login"),
    path("bet", views.bet_request, name="bet"),
    path("", views.login_request, name="login")
]
