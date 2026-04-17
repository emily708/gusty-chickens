from flask import Flask, render_template, request, flash, redirect, session, Blueprint, url_for
from db import *
import random
import json
import random
import constants

with open('data.json', 'r') as file:
    data = json.load(file)

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.before_request
def check_game_state():
    if 'game' in session:
        if 'start' in request.path:
            flash("You already have a game in progress!", "error")
            return redirect('/game/map')
    else:
        if 'start' not in request.path:
            flash("Starting a new game...", "info")
            return redirect('/game/start')

def calculate_odds(passenger):
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
        "tier": {},
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
    percentages["tier"]["value"] = passenger["room"]

    total = 0
    for key in percentages:
        if percentages[key]["value"] == "":
            continue
        percentages[key]["percentage"] = data[key][percentages[key]["value"]]["percentage"]
        total += percentages[key]["percentage"]
    
    percentages["total"] = total / 6
    return percentages

@bp.get('/start')
def start_get():
    game = insert_query("Games", {
        "username": session["username"],
        "currLocation": "Compass Platform"
    })
    session["game"] = game["id"]

    room_use = {}
    for room in constants.rooms["tiers"]:
        room_use[room] = 0

    assignments = []
    passengers = select_query("SELECT * FROM DefaultPassengers")
    for passenger in passengers:
        cabin = passenger["cabin"][0] if len(passenger["cabin"]) > 0 else ""
        
        # Assign Random
        if cabin not in constants.rooms["tiers"].keys():
            if passenger["class"] == 1:
                cabin = random.choice(["A", "B", "C", "D", "E"])
            elif passenger["class"] == 2:
                cabin = random.choice(["C", "D", "E"])
            else:
                cabin = random.choice(["E", "F", "G"])
        
        assignments.append((game["id"], passenger["id"], cabin))
        room_use[cabin] += 1
    
    batch_query("INSERT INTO Passengers (game, id, room) VALUES (?, ?, ?)", assignments)

    data = []
    for room in constants.rooms["tiers"].keys():
        data.append((session["game"], room_use[room], room))
    batch_query("INSERT INTO Rooms (game, usedCapacity, room) VALUES (?, ?, ?)", data)

    return redirect("/game/map")

@bp.get('/loadsave')
def load_save():
    temp = select_query("SELECT * FROM Games WHERE username=?", (session["username"],))
    if len(temp) != 0:
        session["game"] = temp[0]
        return redirect("/game/map")
    else:
        flash("You don't have a saved game!", 'error')
        return redirect(url_for("load_get"))

@bp.get('/map')
def map_get():
    game = session["game"]
    return render_template("map.html")

@bp.get('/end')
def end_get():
    general_query("UPDATE Games SET active=FALSE WHERE id=?", [session["game"]])

    passengers = select_query("SELECT Passengers.id, survived, class, name, sex, age, isAlone, cabin, port, room FROM Passengers INNER JOIN DefaultPassengers ON Passengers.id=DefaultPassengers.id WHERE game=?", [session["game"]])

    for passenger in passengers:
        passenger["odds"] = calculate_odds(passenger)
        if random.random() < passenger["odds"]["total"]:
            passenger["outcome"] = "survived"
        else:
            passenger["outcome"] = "died"

    # Visualize passengers

    session.pop('game', None)
    return render_template("result.html")

@bp.get('/rooms/<place>')
def rooms_get(place):
    general_query("UPDATE Games SET currLocation=? WHERE id=?", (place, session["game"]))

    if place in ["A", "B", "C", "D", "E", "F", "G"]:
        room = select_query("SELECT * FROM Rooms WHERE game=? AND room=?", (session["game"], place))[0]
        room["capacity"] = constants.rooms["tiers"][place]["capacity"]

        passengers = select_query("SELECT Passengers.id, class, name, sex, age, isAlone, cabin, port, room FROM Passengers INNER JOIN DefaultPassengers ON Passengers.id=DefaultPassengers.id WHERE game=? AND room=?", [session["game"], place])

        for passenger in passengers:
            percentages = calculate_odds(passenger)

            labels = []
            values = []
            total = percentages["total"]
            for category, items in percentages.items():
                if category == "total" or "percentage" not in items:
                    continue
                label = f"{category}: {items['value']}"
                difference = items["percentage"] - total
                labels.append(label)
                values.append(difference)

            passenger["labels"] = labels
            passenger["values"] = values

        return render_template("rooms/tier.html", passengers=passengers, room=room)

@bp.post('/move-person')
def move_get():
    passenger = request.form.get("passengerId")
    destination = request.form.get("room")

    if destination == None:
        flash("The passenger is already in this room!", "error")
        return redirect(request.referrer)

    game = select_query("SELECT * FROM Games WHERE id=?", (session["game"],))[0]

    destination_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (destination, session["game"]))[0]

    if destination_room["usedCapacity"] >= constants.rooms["tiers"][destination]["capacity"]:
        flash("Destination room is at capacity! No action performed", "error")
    else:
        general_query("UPDATE Games SET moves=moves-1 WHERE id=?", (session["game"],))
        general_query("UPDATE Rooms SET usedCapacity=usedCapacity-1 WHERE game=? AND room=?",
                        (session["game"], game["currLocation"]))
        general_query("UPDATE Rooms SET usedCapacity=usedCapacity+1 WHERE game=? AND room=?",
                        (session["game"], destination))
        general_query("UPDATE Passengers SET room=? WHERE game=? AND id=?",
                        (destination, session["game"], passenger))
        flash("Move successful!", "success")

    return redirect(request.referrer)

def access_room():
    return render_template(f"{place}.html")
