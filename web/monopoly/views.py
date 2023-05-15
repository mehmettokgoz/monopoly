import random

from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    size = 8
    base = 100
    # TODO: Pull this data from server dynamically
    cell_svg_locations = [(i * base, 0) for i in range(0, size)] + \
                         [((size - 1) * base, i * base) for i in range(1, size)] + \
                         [(i*base, (size - 1) * base) for i in range(size-2, -1, -1)] + \
                         [(0, i * base) for i in range(size - 2, 0, -1)]
    cell_text_locations = [(int(c[0]+base/2), int(c[1]+base/2)) for c in cell_svg_locations]
    print(cell_text_locations)
    colors = ["red", "blue", "yellow"]
    cells = []
    for i in range(size*2+(size-2)*2):
        cells.append({"color": colors[random.randint(0, 2)], "card": "property", "text": i})

    for c in range(len(cells)):
        cells[c]["location"] = cell_svg_locations[c]
        cells[c]["text_location"] = cell_text_locations[c]
    context = {
        "cells": cells,
        "size": size,
        "base": base,
        "width": size * base,
        "height": size * base,
        "cell_number": size*2+(size-2)*2,
        "curr_width": 0,
        "curr_height": base / 2,
        "locations": cell_svg_locations
    }
    print(cell_svg_locations)
    template = loader.get_template("monopoly/index.html")
    return HttpResponse(template.render(context, request))
