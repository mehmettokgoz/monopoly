from django.urls import path

from . import views

urlpatterns = [
    path('board/<slug:board_name>', views.index, name="index"),
    path("", views.list_boards, name="list_boards"),
    path("login", views.login_view, name="login_view"),
    path("auth", views.login_post, name="login_post"),
    path("logout", views.logout, name="logout"),
    path("command/<slug:board_name>", views.execute_command, name="command"),
    path("new", views.new_board, name="new_board")
]
