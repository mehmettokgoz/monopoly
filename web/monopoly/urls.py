from django.urls import path

from . import views

urlpatterns = [
    path('board/<slug:board_name>', views.index, name="index"),
    path("", views.list_boards, name="list_boards"),
    path("login/", views.login_view, name="login_view"),
    path("register", views.register_view, name="start"),
    path("signup", views.register_post, name="start"),
    path("auth", views.login_post, name="login_post"),
    path("logout", views.logout, name="logout"),
    path("command/<slug:board_name>", views.execute_command, name="command"),
    path("new", views.new_board, name="new_board"),
    path("ready/<slug:board_name>", views.ready, name="ready"),
    path("detach/<slug:board_name>", views.detach, name="detach"),
    path("attach/<slug:board_name>", views.attach, name="attach"),
    path("start/<slug:board_name>", views.start, name="start"),
    path("create-template", views.create_template, name="create_template")
]
