from django.urls import path

from . import views

urlpatterns = [
    path("board", views.index, name="index"),
    path("", views.list_boards, name="list_boards"),
    path("login", views.login_view, name="login_view"),
    path("auth", views.login_post, name="login_post"),
    path("logout", views.logout, name="logout"),
]
