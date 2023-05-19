import datetime
import random
import socket
from threading import Condition, Lock, Thread

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect

from monopoly.client import MonopolyClient

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


def index(request):
    size = 8
    base = 100

    # TODO: Pull this data from server dynamically
    cell_svg_locations = [(i * base, 0) for i in range(0, size)] + \
                         [((size - 1) * base, i * base) for i in range(1, size)] + \
                         [(i * base, (size - 1) * base) for i in range(size - 2, -1, -1)] + \
                         [(0, i * base) for i in range(size - 2, 0, -1)]
    cell_text_locations = [(int(c[0] + base / 2), int(c[1] + base / 2)) for c in cell_svg_locations]
    cells = sample_board

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
        cells[c]["location"] = cell_svg_locations[c]
        cells[c]["text_location"] = cell_text_locations[c]
    options = [
        {"name" : "dice", "input" : "no"},
        {"name" : "buy", "input" : "no"},
        {"name" : "upgrade", "input" : "no"},
        {"name" : "bail", "input" : "no"},
        {"name" : "teleport", "input" : "yes"},
        {"name" : "pick", "input" : "yes"}
    ]
    context = {
        "cells": cells,
        "options": options,
        "size": size,
        "base": base,
        "middle_rect_size": (size - 2) * base,
        "middle_text_loc": base + (size - 2) * base / 2,
        "width": size * base,
        "height": size * base,
        "cell_number": size * 2 + (size - 2) * 2,
        "curr_width": 0,
        "curr_height": base / 2,
        "locations": cell_svg_locations
    }
    print(cell_svg_locations)
    template = loader.get_template("monopoly/index.html")
    return HttpResponse(template.render(context, request))


def list_boards(request):
    # TODO: Pull list data here from server
    context = {}
    print(request.COOKIES)
    token = request.COOKIES.get('token')
    if token:

        client = MonopolyClient(4524)
        response = client.send_command(f"list")
        print(response)
        client.close()
        return render(request, "monopoly/list.html", context)
    else:
        return render(request, "monopoly/login.html", {'message': ''})


def login_view(request):
    return render(request, 'monopoly/login.html', {'message': ''})


def login_post(request):
    username = request.POST['username']
    password = request.POST['password']
    print(username, password)
    user = 1
    # TODO: Send actual command for auth
    print(user)
    if user is not None:
        # test if user is not disabled by admin
        request.session["token"] = "TOKEN"
        t = loader.get_template('monopoly/list.html')
        response = HttpResponse(t.render({}, request))
        response.set_cookie('token', 'TOKEN')
        return response
    else:
        return render(request, 'monopoly/login.html', {'message': 'Invalid username or password'})


def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('token')
    return response
