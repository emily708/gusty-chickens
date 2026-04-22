from flask import Flask, render_template, request, flash, redirect, session, Blueprint, url_for
from db import *
import random
import json
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
    insert_query("Items", {
        "name": "Youth Potion",
        "game": session["game"],
        "amount": 1,
    })
    insert_query("Items",
    {
        "name": "First Class Ticket",
        "game": session["game"],
        "amount": 0,
    },)
    insert_query("Items",
    {
        "name": "Hammer",
        "game": session["game"],
        "amount": 0,
    },)
    insert_query("Items",
    {
        "name": "Second Class Ticket",
        "game": session["game"],
        "amount": 0,
    },)
    insert_query("Items",
    {
        "name": "Third Class Ticket",
        "game": session["game"],
        "amount": 0,
    },)
    insert_query("Items",
    {
        "name": "Fourth Class Ticket",
        "game": session["game"],
        "amount": 0,
    },)

    room_use = {}
    for room in constants.rooms["tiers"]:
        room_use[room] = 0

    room_use["kitchen"] = 0

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

        assignments.append((game["id"], passenger["id"], cabin, passenger["age"], passenger["class"]))
        room_use[cabin] += 1

    batch_query("INSERT INTO Passengers (game, id, room, age, class) VALUES (?, ?, ?, ?, ?)", assignments)

    data = []
    for room in constants.rooms["tiers"].keys():
        data.append((session["game"], room_use[room], room))
    batch_query("INSERT INTO Rooms (game, usedCapacity, room) VALUES (?, ?, ?)", data)

    mis_room_data = []
    for room in constants.rooms["miscellaneous"].keys():
        mis_room_data.append((session["game"], 0, room))
    batch_query("INSERT INTO Rooms (game, usedCapacity, room) VALUES (?, ?, ?)", mis_room_data)

    return redirect("/game/map")

@bp.get('/map')
def map_get():
    game = select_query("SELECT * FROM Games WHERE id=?" , [session["game"]])[0]
    caps = get_capacity()
    limits = {}

    for room in ["kitchen", "refrigerated_cargo", "gymnasium", "swimming_pool", "squash_court"]:
        limits[room] = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (room, session["game"]))[0]["usedCapacity"]

    return render_template("map.html", caps=caps, game=game, limits=limits)

@bp.get('/end')
def end_get():
    general_query("UPDATE Games SET active=FALSE WHERE id=?", [session["game"]])

    passengers = select_query("SELECT Passengers.id, survived, Passengers.class, name, sex, Passengers.age, isAlone, cabin, port, room, DefaultPassengers.class AS original_class, DefaultPassengers.age AS original_age FROM Passengers INNER JOIN DefaultPassengers ON Passengers.id=DefaultPassengers.id WHERE game=?", [session["game"]])

    actual_survived = 0
    game_survived = 0
    for passenger in passengers:
        passenger["odds"] = calculate_odds(passenger)
        if random.random() < passenger["odds"]["total"]:
            passenger["outcome"] = "survived"
            game_survived += 1
        else:
            passenger["outcome"] = "died"
        if passenger["survived"] == 1:
            actual_survived += 1
        age = passenger["original_age"]
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

        passenger["odds"]["original_age"] = {}
        passenger["odds"]["original_age"]["value"] = age_group
        passenger["odds"]["original_age"]["percentage"] = data["age"][age_group]["percentage"]
        passenger["odds"]["original_class"] = {}
        passenger["odds"]["original_class"]["value"] = str(passenger["original_class"])
        passenger["odds"]["original_class"]["percentage"] = data["class"][str(passenger["original_class"])]["percentage"]

    #print(passengers[0])

    total = len(passengers)
    final = {"actual_survival_rate": actual_survived / total, "game_survival_rate": game_survived / total}
    session.pop('game', None)
    return render_template("result.html", final=final, passengers=passengers)

@bp.get('/rooms/<place>')
def rooms_get(place):
    game = select_query("SELECT * FROM Games WHERE id=?", (session["game"],))[0]
    inventory = select_query("SELECT * FROM Items WHERE game=? AND amount>0", (session["game"],))

    if place != game["currLocation"]:
        if game["moves"] <= 1:
            flash("You have ran out of moves! Ending game...", "info")
            return redirect(url_for("game.end_get"))
        else:
            general_query("UPDATE Games SET currLocation=? WHERE id=?", (place, session["game"]))
            use_move()
            flash("You have spent one move traveling!", "info")

    if place in ["A", "B", "C", "D", "E", "F", "G"]:
        room = select_query("SELECT * FROM Rooms WHERE game=? AND room=?", (session["game"], place))[0]
        room["capacity"] = constants.rooms["tiers"][place]["capacity"]

        passengers = select_query("SELECT Passengers.id, Passengers.class, name, sex, Passengers.age, isAlone, cabin, port, room FROM Passengers INNER JOIN DefaultPassengers ON Passengers.id=DefaultPassengers.id WHERE game=? AND room=?", [session["game"], place])

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

    elif place == "kitchen":
        kitchen = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (place, session["game"]))[0]
        if (constants.rooms["miscellaneous"][place]["limit"] != 0) and (kitchen["usedCapacity"] >= constants.rooms["miscellaneous"][place]["limit"]):
            flash("You have already used the kitchen 5 times this round!", "info")
            return redirect(request.referrer)

        use_move()
        general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE room=? AND game=?", (place, session["game"]))

        kitchen = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (place, session["game"]))[0]

        num = random.random()
        if num < 0.5:
            general_query("UPDATE Games SET moves=moves+5 WHERE id=?", (session["game"],))
            flash("There was food! You have restored 5 moves!", "info");
        elif num < 0.9:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Growth Potion", session["game"]))
            flash("A chef gives you a specially prepared growth potion!", "info")
        else:
            flash("The kitchen didn't have any food. You wasted your time!", "info");

    elif place == "compass_platform":
        use_move()

        num = random.random()
        if num < 0.67: #67%
            flash("Nothing happened :(", "info");
            return redirect(url_for("game.map_get"))
        elif num < 0.82: #15%
            general_query("UPDATE Games SET moves=moves-1 WHERE id=?", (session["game"],))
            flash("Uh oh! Bad luck strikes and you lost an additional move!", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.92: #10%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Youth Potion", session["game"]))
            flash("A death knell rings. You magically recieve a Youth potion.", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.97: #5%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("First Class Ticket", session["game"]))
            flash("You won a first class ticket! Now you can send someone to tier A for free.", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.99: #2%
            general_query("UPDATE Games SET active=FALSE WHERE id=?", (session["game"],))
            flash("You rolled instant death? You sick, sick gambler.", "info")
            return redirect(url_for("game.end_get"))
        else:
            general_query("UPDATE Games SET active=FALSE, moves=9999 WHERE id=?", (session["game"],))
            flash("YAYY YOU WINNN YOU LUCKY BASTARD!!!", "info")
            return redirect(url_for("game.end_get"))

    elif place == "refrigerated_cargo":
        this_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (place, session["game"]))[0]
        if (constants.rooms["miscellaneous"][place]["limit"] != 0) and (this_room["usedCapacity"] >= constants.rooms["miscellaneous"][place]["limit"]):
            flash("You have already refilled the kitchen once this round!", "info")
            return redirect(request.referrer)

        use_move()
        general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE room=? AND game=?", (place, session["game"]))
        # NEED TO UPDATE CAP FOR KITCHEN
        general_query("UPDATE Rooms SET usedCapacity = 0 WHERE room=? AND game=?", ("kitchen", session["game"],))

    elif place == "water_tank" or place == "boiler_room":
        this_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (place, session["game"]))[0]
        if (constants.rooms["miscellaneous"][place]["limit"] != 0) and (this_room["usedCapacity"] >= constants.rooms["miscellaneous"][place]["limit"]):
            flash("You cannot go in to these rooms anymore!", "info")
            return redirect(request.referrer)

        use_move()
        general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE room=? AND game=?", (place, session["game"]))

        num = random.random()
        if num < 0.30: #30%
            # ONLY ONE PERMANENT HAMMER ALLOWED
            get_num = select_query("SELECT amount FROM Items WHERE name=? and game=?", ("Hammer", session["game"]))[0]["amount"]
            if get_num < 1:
                general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Hammer", session["game"]))
                flash("You obtained a permanent hammer! Now you can break into rooms without costing a move :D", "info")
            else:
                flash("You already have a hammer...", "info")
            return redirect(url_for("game.map_get"))
        else: #70%
            flash("You wandered around and... found nothing.", "info")
            return redirect(url_for("game.map_get"))

    elif place in ["gymnasium", "swimming_pool", "squash_court"]:
        this_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (place, session["game"]))[0]
        if (constants.rooms["miscellaneous"][place]["limit"] != 0) and (this_room["usedCapacity"] >= constants.rooms["miscellaneous"][place]["limit"]):
            flash("You over-exercised!", "info")
            return redirect(request.referrer)

        use_move()

        general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE room=? AND game=?", (place, session["game"]))
        num = random.random()
        if num < 0.50:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Growth Potion", session["game"]))
            flash("Make your enemies older hehehe... you got a growth potion!", "info");
            return redirect(url_for("game.map_get"))
        else:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Youth Potion", session["game"]))
            flash("A mysterious elder in a cloak hands you a youth potion.", "info");
            return redirect(url_for("game.map_get"))

    elif place == "library":
        use_move()

        num = random.random()
        if num < 0.60: #60%
            flash("Too bad, too sad, nothing happened.", "info");
            return redirect(url_for("game.map_get"))
        elif num < 0.85: #25%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Fourth Class Ticket", session["game"]))
            flash("You found an N item at first glance: Fourth Class Ticket!", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.95: #10%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Third Class Ticket", session["game"]))
            flash("You found an R item while flipping through the books: Third Class Ticket!", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.995: #4.5%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Second Class Ticket", session["game"]))
            flash("You read dozens of books, and find an SR item: Second Class Ticket!", "info")
            return redirect(url_for("game.map_get"))
        else: #0.5%
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("First Class Ticket", session["game"]))
            flash("Wowie, you absolute reading fanatic! You found an SSR item: First Class Ticket!", "info")
            return redirect(url_for("game.end_get"))

    elif place == "crew_room" or place == "post_office":
        use_move()

        num = random.random()
        if num < 0.70:
            flash("You found canned air. How? Why?", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.90:
            flash("You find some snake wine and dried cane toads. Curious, you ate them all. Nothing happened.", "info")
            return redirect(url_for("game.map_get"))
        elif num < 0.95:
            general_query("UPDATE Items SET amount=amount+2 WHERE name=? AND game=?", ("Youth Potion", session["game"]))
            flash("You find two youth potions in some unsavory magazines!", "info")
            return redirect(url_for("game.map_get"))
        else:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", ("Growth Potion", session["game"]))
            flash("You shuffle around, and your foot hits something. A growth potion!", "info")
            return redirect(url_for("game.map_get"))

    elif place == "cargo":
        use_move()
        flash("You look through the shelves and find ABSOLUTELY NOTHING :)", "info")

    return redirect(url_for("game.map_get"))


@bp.post('/use-item')
def use_get():
    passenger = request.form.get("passengerId")
    item_name = request.form.get("item")
    general_query("UPDATE Items SET amount=amount-1 WHERE name=? AND game=?", (item_name, session["game"]))

    pass_dict = select_query("SELECT * FROM Passengers WHERE game=? AND id=?", (session["game"], passenger))[0]

    if item_name == "Growth Potion":
        general_query("UPDATE Passengers SET age=age+10 WHERE id=? AND game=?", (passenger, session["game"]))
        flash("You used a growth potion to make this person 10 years older!", "info")

    elif item_name == "Youth Potion":
        if pass_dict["age"] <= 13:
            flash("You wasted your youth potion on a child! Shameful.", "info")
        else:
            general_query("UPDATE Passengers SET age=age-10 WHERE id=? AND game=?", (passenger, session["game"]))
            flash("You made this passenger 10 years younger! WOW", "info")

    elif item_name == "First Class Ticket":
        tier = 'A'
        tier_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (tier, session["game"]))[0]

        if tier_room["usedCapacity"] >= constants.rooms["tiers"][tier]["capacity"]:
            general_query("UPDATE Items SET amount=amount+1 WHERE name=? AND game=?", (item_name, session["game"]))
            flash("Dearest VVIP customer, Tier A is full. Here is your ticket refund.", "error")
        else:
            general_query("UPDATE Passengers SET room=? WHERE game=? AND id=?", (tier, session["game"], passenger))
            general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE game=? AND room=?", (session["game"], tier))
            flash("Ticket used! Passenger has moved to Tier A.", "info")

    elif item_name == "Second Class Ticket":
        tier = 'B'
        tier_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (tier, session["game"]))[0]

        if tier_room["usedCapacity"] >= constants.rooms["tiers"][tier]["capacity"]:
            general_query("UPDATE Items SET amount=amount-1 WHERE name=? AND game=?", (item_name, session["game"]))
            flash("Dear VIP customer, we are sorry, Tier B is full. Here is your ticket refund.", "error")
        else:
            general_query("UPDATE Passengers SET room=? WHERE game=? AND id=?", (tier, session["game"], passenger))
            general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE game=? AND room=?", (session["game"], tier))
            flash("Ticket used! Passenger has moved to Tier B.", "info")

    elif item_name == "Third Class Ticket":
        tier = 'C'
        tier_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (tier, session["game"]))[0]

        if tier_room["usedCapacity"] >= constants.rooms["tiers"][tier]["capacity"]:
            flash("Unfortunately, Tier C is full, and the ticket is not refunded.", "error")
        else:
            general_query("UPDATE Passengers SET room=? WHERE game=? AND id=?", (tier, session["game"], passenger))
            general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE game=? AND room=?", (session["game"], tier))
            flash("Ticket used! Passenger has moved to Tier C.", "info")

    elif item_name == "Fourth Class Ticket":
        tier = 'D'
        tier_room = select_query("SELECT * FROM Rooms WHERE room=? AND game=?", (tier, session["game"]))[0]

        if tier_room["usedCapacity"] >= constants.rooms["tiers"][tier]["capacity"]:
            flash("Ticket failed and not refunded. Tier D is full!", "error")
        else:
            general_query("UPDATE Passengers SET room=? WHERE game=? AND id=?", (tier, session["game"], passenger))
            general_query("UPDATE Rooms SET usedCapacity = usedCapacity + 1 WHERE game=? AND room=?", (session["game"], tier))
            flash("Ticket used! Passenger has moved to Tier D.", "info")

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
        use_move()
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

# check if need to spend a move
def use_move():
    # check moves is not negative
    current = select_query("SELECT moves FROM Games WHERE id=?", (session["game"],))[0]
    if current["moves"] <= 0:
        flash("Out of moves!", "info")
        general_query("UPDATE Games SET moves=0 WHERE id=?", (session["game"],))
        return False

    if not has_hammer():
        # consume a move
        general_query("UPDATE Games SET moves = moves - 1 WHERE id = ?", (session["game"],))

def has_hammer():
    a = select_query("SELECT amount FROM Items WHERE name=? AND game=?", ("Hammer", session["game"]) )[0]["amount"]
    return a > 0

def check_move_used(place):
    if place in constants.rooms["miscellaneous"]:
        use_move()

@bp.get("/reset")
def reset_game():
    if "game" in session:
        session.pop("game", None)
    return redirect(url_for("game.start_get"))
