from db import insert_query, general_query, select_query
import pprint

# calculating rooms
rooms = select_query("SELECT survived,cabin FROM DefaultPassengers WHERE cabin IS NOT NULL AND cabin!=''")

tier_rates = {}

for letter in ["A", "B", "C", "D", "E", "F", "G"]:
    tier_rates[letter] = {
        "total": 0,
        "survived": 0
    }

for room in rooms:
    room["cabin"] = room["cabin"].split()
    for cabin in room["cabin"]:
        if cabin[0] not in tier_rates:
            continue
        tier_rates[cabin[0]]["survived"] += room["survived"]
        tier_rates[cabin[0]]["total"] += 1

for tier in tier_rates:
    tier_rates[tier]["percentage"] = tier_rates[tier]["survived"] / tier_rates[tier]["total"]

gender_rates = {}

for gender in ["male", "female"]:
    gender_rates[gender] = {
        "total": 0,
        "survived": 0
    }

passengers = select_query("SELECT * FROM DefaultPassengers")

for passenger in passengers:
    gender_rates[passenger["sex"]]["survived"] += passenger["survived"]
    gender_rates[passenger["sex"]]["total"] += 1

for gender in gender_rates:
    gender_rates[gender]["percentage"] = gender_rates[gender]["survived"] / gender_rates[gender]["total"]

age_rates = {}

for age_group in ["child", "teenager", "young adult", "adult", "senior"]:
    age_rates[age_group] = {
        "total": 0,
        "survived": 0
    }

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

for age_group in age_rates:
    age_rates[age_group]["percentage"] = age_rates[age_group]["survived"] / age_rates[age_group]["total"]

pprint.pprint(tier_rates)
pprint.pprint(gender_rates)
pprint.pprint(age_rates)
