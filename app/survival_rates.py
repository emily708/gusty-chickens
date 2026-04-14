from db import insert_query, general_query, select_query
import pprint
import json

def initialize(arr):
    d = {}
    for key in arr:
        d[key] = {
            "total": 0,
            "survived": 0
        }
    return d

# calculating rooms
rooms = select_query("SELECT survived,cabin FROM DefaultPassengers WHERE cabin IS NOT NULL AND cabin!=''")

tier_rates = initialize(["A", "B", "C", "D", "E", "F", "G"])

for room in rooms:
    room["cabin"] = room["cabin"].split()
    for cabin in room["cabin"]:
        if cabin[0] not in tier_rates:
            continue
        tier_rates[cabin[0]]["survived"] += room["survived"]
        tier_rates[cabin[0]]["total"] += 1

gender_rates = initialize(["male", "female"])

passengers = select_query("SELECT * FROM DefaultPassengers")

for passenger in passengers:
    gender_rates[passenger["sex"]]["survived"] += passenger["survived"]
    gender_rates[passenger["sex"]]["total"] += 1

age_rates = initialize(["child", "teenager", "young adult", "adult", "senior"])

for passenger in passengers:
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
    age_rates[age_group]["survived"] += passenger["survived"]
    age_rates[age_group]["total"] += 1

alone_rates = initialize(["true", "false"])

alone_rates["true"]["survived"] = select_query("SELECT COUNT(*) FROM DefaultPassengers WHERE survived=1 AND isAlone=1")[0]["COUNT(*)"]
alone_rates["false"]["survived"] = select_query("SELECT COUNT(*) FROM DefaultPassengers WHERE survived=1 AND isAlone=0")[0]["COUNT(*)"]
alone_rates["true"]["total"] = select_query("SELECT COUNT(*) FROM DefaultPassengers WHERE isAlone=1")[0]["COUNT(*)"]
alone_rates["false"]["total"] = select_query("SELECT COUNT(*) FROM DefaultPassengers WHERE isAlone=0")[0]["COUNT(*)"]

class_rates = initialize([1, 2, 3])

for passenger in passengers:
    class_rates[passenger["class"]]["survived"] += passenger["survived"]
    class_rates[passenger["class"]]["total"] += 1

port_rates = initialize(["Q", "S", "C"])

for passenger in passengers:
    if passenger["port"] not in port_rates:
        continue
    port_rates[passenger["port"]]["survived"] += passenger["survived"]
    port_rates[passenger["port"]]["total"] += 1

rates = {
    "tier": tier_rates,
    "gender": gender_rates,
    "age": age_rates,
    "isAlone": alone_rates,
    "class": class_rates,
    "port": port_rates
}

for category in rates:
    for sub in rates[category]:
        rates[category][sub]["percentage"] = rates[category][sub]["survived"] / rates[category][sub]["total"]

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(rates, f, indent=4)