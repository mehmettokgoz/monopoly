import datetime
import json
import random
import socket
from threading import Condition, Lock, Thread

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from monopoly.client import MonopolyClient
from monopoly.protocol import NewBoardCodec, StartGameCodec, ListBoardCodec, OpenBoardCodec, \
    CloseBoardCodec, AuthCodec, CommandCodec, ReadyBoardCodec, UnwatchBoardCodec, WatchBoardCodec

port = 1297

sample_board = [
    {"color": "blue", "card": "start", "text": 1, },
    {"color": "#995237", "card": "property", "text": 2, "money": 123},
    {"color": "#995237", "card": "chance", "text": 3},
    {"color": "#995237", "card": "property", "text": 4},
    {"color": "blue", "card": "chance", "text": 5},
    {"color": "#aae1ff", "card": "property", "text": 6},
    {"color": "#aae1ff", "card": "property", "text": 7},
    {"color": "blue", "card": "go_to_jail", "text": 8},
    {"color": "#db3a93", "card": "property", "text": 9},
    {"color": "#db3a93", "card": "property", "text": 10},
    {"color": "blue", "card": "chance", "text": 11},
    {"color": "#f69421", "card": "property", "text": 12},
    {"color": "#f69421", "card": "property", "text": 13},
    {"color": "#f69421", "card": "property", "text": 14},
    {"color": "blue", "card": "parking", "text": 15},
    {"color": "#ec1a24", "card": "property", "text": 16},
    {"color": "#ec1a24", "card": "property", "text": 17},
    {"color": "blue", "card": "chance", "text": 18},
    {"color": "#fff100", "card": "property", "text": 19},
    {"color": "#fff100", "card": "property", "text": 20},
    {"color": "#fff100", "card": "property", "text": 21},
    {"color": "blue", "card": "go_to_jail", "text": 22},
    {"color": "#1db35b", "card": "property", "text": 23},
    {"color": "#1db35b", "card": "property", "text": 24},
    {"color": "blue", "card": "chance", "text": 25},
    {"color": "#0572b8", "card": "property", "text": 26},
    {"color": "blue", "card": "chance", "text": 27},
    {"color": "#0572b8", "card": "property", "text": 28},
]


def index(request, board_name):
    size = 8
    base = 100

    token = request.COOKIES.get('token')
    if token:
        client = MonopolyClient(port)
        response = client.send_command(token, "state", board_name)
        response = json.loads(response)

        client.close()
    else:
        return render(request, "monopoly/login.html", {'message': 'You need to log in to execute commands on board.'})

    # TODO: Pull this data from server dynamically
    cell_svg_locations = [(i * base, 0) for i in range(0, size)] + \
                         [((size - 1) * base, i * base) for i in range(1, size)] + \
                         [(i * base, (size - 1) * base) for i in range(size - 2, -1, -1)] + \
                         [(0, i * base) for i in range(size - 2, 0, -1)]
    cell_text_locations = [(int(c[0] + base / 2), int(c[1] + base / 2)) for c in cell_svg_locations]
    cells = response["cells"]
    print(response)
    for i in range(size * 2 + (size - 2) * 2):
        if i == 0 or i == size - 1 or i == 2 * size - 2 or i == 3 * size - 3:
            cells[i]["direction"] = "corner"
        elif i < size:
            cells[i]["direction"] = "up"
        elif size <= i < (2 * size - 2):
            cells[i]["direction"] = "right"
        elif 2 * size - 1 <= i <= 3 * size - 3:
            cells[i]["direction"] = "bottom"
        else:
            cells[i]["direction"] = "left"
    for c in range(len(cells)):
        cells[c]["index"] = c
        cells[c]["location"] = cell_svg_locations[c]
        cells[c]["text_location"] = cell_text_locations[c]

    for user_index in response["user_positions"].keys():
        response["user_positions"][user_index] = cells[response["user_positions"][user_index]]["text_location"]

    global curr_chance_card
    curr_chance_card = response["curr_chance_card"]

    context = {
        "username": request.COOKIES.get("username"),
        "name": board_name,
        "users": response["users"],
        "current_user": response["current_user"],
        "curr_chance_card": response["curr_chance_card"],
        "options": response["options"],
        "user_positions": response["user_positions"],
        "cells": cells,
        "size": size,
        "base": base,
        "game_over": response["game_over"],
        "middle_rect_size": (size - 2) * base,
        "middle_text_loc": base + (size - 2) * base / 2,
        "width": size * base,
        "height": size * base,
        "cell_number": size * 2 + (size - 2) * 2,
        "curr_width": 0,
        "curr_height": base / 2,
        "locations": cell_svg_locations
    }

    template = loader.get_template("monopoly/index.html")
    return HttpResponse(template.render(context, request))


def list_boards(request):
    # TODO: Pull list data here from server
    context = {}
    token = request.COOKIES.get('token')
    client = MonopolyClient(port)
    if token is not None:
        response = client.send_command(token, "list")
        client.close()
        response = response.decode().split(",")
        if len(response) <= 0:
            return render(request, "monopoly/list.html",
                          {"username": request.COOKIES.get("username"), 'message': 'No board is available.',
                           "boards": []})
        else:
            return render(request, "monopoly/list.html",
                          {"username": request.COOKIES.get("username"), 'message': "", "boards": response})
    else:
        return HttpResponseRedirect("/login")


def execute_command(request, board_name):
    context = {}
    option = request.POST["option"]
    selected_cell = request.POST["selected_cell"]
    token = request.COOKIES.get('token')
    if token:
        client = MonopolyClient(port)
        # TODO: Send related command by taking from request.
        print(selected_cell)
        response = client.send_command(token, "command", option, selected_cell)
        print(response)
        client.close()
        # TODO: Redirect connection to board page.
        return HttpResponseRedirect(f'/board/{board_name}')
        # return render(request, "monopoly/board.html", context)
    else:
        return render(request, "monopoly/login.html", {'message': 'You need to log in to execute commands on board.'})


def login_view(request):
    return render(request, 'monopoly/login.html', {'message': ''})


def login_post(request):
    username = request.POST['username']
    password = request.POST['password']


    # test if user is not disabled by admin
    client = MonopolyClient(port)
    response = client.send_command("NO_TOKEN_REQUIRED", "auth", username, password)

    token_response = response.decode()
    if len(token_response) > 20:
        return render(request, 'monopoly/login.html', {'message': token_response})

    client.close()

    response = HttpResponseRedirect("/")
    response.set_cookie('token', token_response)
    response.set_cookie('username', username)
    return response


def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('token')
    response.delete_cookie('username')
    return response


def new_board(request):
    board_json = request.POST['json_board']
    name = request.POST['name']


    # TODO: Pull list data here from server
    context = {}

    token = request.COOKIES.get('token')
    client = MonopolyClient(port)
    if token is not None:
        response = client.send_command(token, "new", name, board_json)
        client.close()

        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/login")


def ready(request, board_name):
    # TODO: Pull list data here from server
    context = {}
    token = request.COOKIES.get('token')
    client = MonopolyClient(port)
    if token is not None:
        response = client.send_command(token, "ready", board_name)
        client.close()
        return HttpResponseRedirect(f"/board/{board_name}")
    else:
        return HttpResponseRedirect("/login")


def attach(request, board_name):
    # TODO: Pull list data here from server
    context = {}
    token = request.COOKIES.get('token')
    client = MonopolyClient(port)

    if token is not None:
        response = client.send_command(token, "open", board_name)
        client.close()
        return HttpResponseRedirect(f"/board/{board_name}")
    else:
        return HttpResponseRedirect("/login")


def detach(request, board_name):
    # TODO: Pull list data here from server
    context = {}
    token = request.COOKIES.get('token')
    client = MonopolyClient(port)
    if token is not None:
        response = client.send_command(token, "close", board_name)
        client.close()
        return HttpResponseRedirect(f"/board/{board_name}")
    else:
        return HttpResponseRedirect("/login")


def start(request, board_name):
    context = {}
    token = request.COOKIES.get('token')
    client = MonopolyClient(port)
    if token is not None:
        response = client.send_command(token, "start", board_name)
        client.close()
        return HttpResponseRedirect(f"/board/{board_name}")
    else:
        return HttpResponseRedirect("/login")
