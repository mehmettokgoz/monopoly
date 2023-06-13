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
from django.utils.datastructures import MultiValueDictKeyError

from monopoly.client import MonopolyClient
from monopoly.protocol import NewBoardCodec, StartGameCodec, ListBoardCodec, OpenBoardCodec, \
    CloseBoardCodec, AuthCodec, CommandCodec, ReadyBoardCodec, UnwatchBoardCodec, WatchBoardCodec

port = 1567


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
    cells = response["cells"]

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

    cell_text_locations = []
    for i in range(len(cell_svg_locations)):
        c = cell_svg_locations[i]
        if cells[i]["type"] == "property":
            if cells[i]["direction"] == "corner":
                cell_text_locations.append((int(c[0] + base / 2), int(c[1] + base / 2)))
            elif cells[i]["direction"] == "up":
                cell_text_locations.append((int(c[0] + base / 2), int(c[1] + 20)))
            elif cells[i]["direction"] == "right":
                cell_text_locations.append((int(c[0] + 40), int(c[1] + base / 2)))
            elif cells[i]["direction"] == "bottom":
                cell_text_locations.append((int(c[0] + base / 2), int(c[1] + 40)))
            elif cells[i]["direction"] == "left":
                cell_text_locations.append((int(c[0]) + 60, int(c[1] + base / 2)))
        else:
            cell_text_locations.append((int(c[0] + base / 2), int(c[1] + base / 2)))

    for c in range(len(cells)):
        cells[c]["index"] = c
        cells[c]["location"] = cell_svg_locations[c]
        cells[c]["text_location"] = cell_text_locations[c]

    for user_index in response["user_positions"].keys():
        response["user_positions"][user_index] = cells[response["user_positions"][user_index]]["text_location"]
    print(response)
    curr_chance_card = None
    if response["curr_chance_card"] != '' or response["curr_chance_card"] != "":
        curr_chance_card = response["curr_chance_card"]

    context = {
        "username": request.COOKIES.get("username"),
        "name": board_name,
        "users": response["users"],
        "current_user": response["current_user"],
        "curr_chance_card": curr_chance_card,
        "options": response["options"],
        "user_positions": response["user_positions"],
        "started": response["started"],
        "total_size": len(cells),
        "cells": cells,
        "size": size,
        "base": base,
        "token": token,
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
        print(response)
        client.close()
        response = response.decode().split(",")
        if response[0] == "No board is available.":
            return render(request, "monopoly/list.html",
                          {"username": request.COOKIES.get("username"),
                           'message': 'No board is available. You can create a new board.',
                           "boards": []})
        else:
            response_dict = []
            for i in response:
                i = i.split(":")
                response_dict.append({"name": i[0], "users": i[1], "ready": i[2], "started": i[3]})
            return render(request, "monopoly/list.html",
                          {"username": request.COOKIES.get("username"), 'message': "", "boards": response_dict})
    else:
        return HttpResponseRedirect("/login")


def execute_command(request, board_name):
    context = {}
    option = request.POST["option"]
    selected_cell = 0
    try:
        selected_cell = request.POST["selected_cell"]
    except MultiValueDictKeyError as e:
        selected_cell = 0
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


def register_view(request):
    return render(request, 'monopoly/register.html', {'message': ''})


def register_post(request):
    username = request.POST['username']
    email = request.POST['email']
    full_name = request.POST['full_name']
    password = request.POST['password']

    print(username, email, full_name, password)

    client = MonopolyClient(port)
    response = client.send_command("NO_TOKEN_REQUIRED", "register", username, email, full_name, password)
    client.close()
    response = HttpResponseRedirect("/")
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


def create_template(request):
    context = {}
    return render(request, "monopoly/create-board.html", context)