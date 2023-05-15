from django.urls import path

from . import views

urlpatterns = [
    path("board", views.index, name="index"),
    path("", views.list_boards, name="list_boards")
]
