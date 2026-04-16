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
    passenger = select_query("SELECT * FROM Passengers WHERE game=? AND id=?", [session["game"], passenger_id])[0]
    percentages["tier"]["value"] = passenger["room"]
    total = 0
    for key in percentages:
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
    if place in ["A", "B", "C", "D", "E", "F", "G"]:
        room = select_query("SELECT * FROM DefaultRooms WHERE name=?", [place])[0]
        capacity = room["capacity"]

        passengers = select_query("SELECT Passengers.id, class, name, sex, age, isAlone, cabin, port, room FROM Passengers INNER JOIN DefaultPassengers ON Passengers.id=DefaultPassengers.id WHERE game=? AND room=?", [session["game"], place])

        for passenger in passengers:
            passenger["odds"] = calculate_odds(passenger["id"])

        return render_template("rooms/tier.html", passengers=passengers, room=room)

@bp.post('/move-person')
def move_get():
    passenger = request.form.get("passengerId")
    destination = request.form.get("room")

    # Update Actions
    
    # Flash Response

    flash("outcome", "success")
    return redirect(request.referrer)

def access_room():
    return render_template(f"{place}.html")

@bp.get("/chart/example")
#sample chart w percentages for each trait
def chart_get():
    labels = []
    values = []
    for category, items in data.items():
        for value, stats in items.items():
            labels.append(f"{category}: {value}")
            values.append(stats["percentage"])
    return render_template("chart.html", labels=labels, values=values)

#chart by passenger_id
@bp.get("/chart/<int:passenger_id>")
def passenger_chart_get(passenger_id):
    percentages = calculate_odds(passenger_id)
    labels = []
    values = []
    total = percentages["total"]
    for category, items in percentages.items():
        if category == "total":
            continue
        label = f"{category}: {items['value']}"
        difference = items["percentage"] - total
        labels.append(label)
        values.append(difference)
    return render_template("chart.html", labels = labels, values = values)
