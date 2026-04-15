from flask import Flask, render_template, request, flash, redirect, session, Blueprint
from db import select_query, insert_query, general_query
import random
import json

with open('data.json', 'r') as file:
    data = json.load(file)

bp = Blueprint('game', __name__, url_prefix='/game')

def calculate_odds(passenger_id):
    passenger = select_query("SELECT * FROM DefaultPassengers WHERE id=?", [passenger_id])[0]
    percentages = {
        "class": {
            "value": str(passenger["class"]),
        },
        "port": {
            "value": str(passenger["port"]),
        },
        "gender": {
            "value": str(passenger["sex"]),
        },
        "isAlone": {},
        "age": {},
        "tier": {}
    }
    percentages["isAlone"]["value"] = "true" if passenger["isAlone"] == 1 else "false"
    age = passenger["age"]
    if age <= 12:
        age_group = "child"
    elif age <= 19:
        age_group = "teenager"
    elif age <= 35:
        age_group = "young adult"
    elif age <= 64:
        age_group = "adult"
    else:
        age_group = "senior"
    percentages["age"]["value"] = age_group
    passenger = select_query("SELECT * FROM Passengers WHERE game=? AND id=?", [session["game"], passenger_id])[0]
    percentages["tier"]["value"] = passenger["room"]
    for key in percentages:
        percentages[key]["percentage"] = data[key][percentages[key]["value"]]["percentage"]
    return percentages

@bp.get('/start')
def start_get():
    game = insert_query("Games", {
        "username": session["username"],
        "currLocation": "Compass Platform"
    })
    session["game"] = game["id"]
    passengers = select_query("SELECT * FROM DefaultPassengers")
    for passenger in passengers:
        cabin = passenger["cabin"][0] if len(passenger["cabin"]) > 0 else ""
        if cabin not in ["A", "B", "C", "D", "E", "F", "G"]:
            if passenger["class"] == 1:
                cabin = random.choice(["A", "B", "C", "D", "E"])
            elif passenger["class"] == 2:
                cabin = random.choice(["C", "D", "E"])
            else:
                cabin = random.choice(["E", "F", "G"])
        insert_query("Passengers", {
            "game": game["id"],
            "id": passenger["id"],
            "room": cabin,
        })
    calculate_odds(10)
    return redirect("/game/map")

@bp.get('/map')
def map_get():
    game = session["game"]
    return render_template("map.html")

@bp.get('/end')
def end_get():
    general_query("UPDATE Games SET active=FALSE WHERE id=?", [session["game"]])
    return redirect("/")

@bp.get('/rooms/<place>')
def rooms_get(place):
    room_names = DefaultRooms().get(name)
    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        # get passengers for the room accessed

        # parse and display on a table in html file

        # add a checkbox next to each passenger to move
    return access_room(place)

def access_room():
    return render_template(f"{place}.html")
