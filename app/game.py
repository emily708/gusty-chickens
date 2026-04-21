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

    # Testing?
    insert_query("Items", {
        "name": "Growth Potion",
        "game": session["game"],
        "amount": 1,
    })

    room_use = {}
    for room in constants.rooms["tiers"]:
        room_use[room] = 0

    room_use["Kitchen"] = 0

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
                cabin = random.choice(["F", "G"])

        assignments.append((game["id"], passenger["id"], cabin))
        room_use[cabin] += 1

    batch_query("INSERT INTO Passengers (game, id, room) VALUES (?, ?, ?)", assignments)

    data = []
    for room in constants.rooms["tiers"].keys():
        data.append((session["game"], room_use[room], room))
    batch_query("INSERT INTO Rooms (game, usedCapacity, room) VALUES (?, ?, ?)", data)

    return redirect("/game/map")

@bp.get('/map')
def map_get():
    game = select_query("SELECT * FROM Games WHERE id=?" , [session["game"]])[0]
    caps = get_capacity()
    return render_template("map.html", caps=caps, game=game)

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
    game = select_query("SELECT * FROM Games WHERE id=?", (session["game"],))[0]
    inventory = select_query("SELECT * FROM Items WHERE game=? AND amount>0", (session["game"],))

    if place != game["currLocation"]:
        if game["moves"] <= 1:
            flash("You have ran out of moves! Ending game...", "info")
            return redirect(url_for("end_get"))
        else:
            general_query("UPDATE Games SET currLocation=?, moves=moves-1 WHERE id=?", (place, session["game"]))
            game["moves"] -= 1
            flash("You have spent one move traveling!", "info")

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

        return render_template("rooms/tier.html", passengers=passengers, room=room, game=game, inventory=inventory)

    elif place == "Kitchen":
        kitchen = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", ("Kitchen", sesison["game"]))
        if kitchen["usedCapacity"] >= constants.rooms["miscellaneous"]["kitchen"]["limit"]:
            flash("You have already used the kitchen 5 times this round!")
            return redirect(request.referrer)

        num = random.random()
        if num < 0.5:
            general_query("UPDATE Games SET moves=moves+5 WHERE id=?", (session["game"],))
            flash("There was food! You have restored 5 moves!");
        elif num < 0.9:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Growth Potion", session["game"]))
            flash("A chef gives you a specially prepared growth potion!")
        else:
            flash("The kitchen didn't have any food. You wasted your time!");

        return redirect(request.referrer)


@bp.post('/use-item')
def use_get():
    passenger = request.form.get("passengerId")
    item_name = request.form.get("item")
    general_query("UPDATE Items SET amount=amount-1 WHERE name=? AND game=?", (item_name, session["game"]))

    flash("Item used!", "info")
    return redirect(request.referrer)

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

def get_capacity():
    # {room name: [curr cap, total cap]}
    currCap = {}
    passengers = select_query("SELECT room FROM Passengers WHERE game = ?", [session["game"]])
    passList = [] # list of room values

    for i in passengers:
        passList.append(i['room'])

    for room in constants.rooms["tiers"]:
        # rooms are tiers i.e. A, B, ...
        # val are the total capacities {"capacity": xx}
        val = constants.rooms["tiers"][room]
        count = passList.count(room)
        currCap[room] = [count, val["capacity"]]
    return currCap
