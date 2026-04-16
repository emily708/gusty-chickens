import csv
import constants
from db import *
import json

args = []

# Parsing CSVs
with open('titanic1.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    next(reader)
    for row in reader:
        if int(row[0]) > 1309:
            break
        args.append((
            row[0],
            row[1],
            row[2],
            "female" if row[3] == "1" else "male",
            row[4],
            row[10],
            row[9]
        ))

batch_query("INSERT INTO DefaultPassengers (id, survived, class, sex, age, fare, isAlone) VALUES (?, ?, ?, ?, ?, ?, ?)", args)

args = []

with open('titanic2.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    next(reader)
    for row in reader:
        args.append((row[3], row[10], row[11], row[0]))

with open('titanic3.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    next(reader)
    for row in reader:
        args.append((row[3], row[10], row[11], row[0]))

batch_query("UPDATE DefaultPassengers SET name=?, cabin=?, port=? WHERE id=?", args)

# Calculating data.json

def initialize(arr):
    d = {}
    for key in arr:
        d[key] = {
            "total": 0,
            "survived": 0
        }
    return d

rooms = select_query("SELECT survived,cabin FROM DefaultPassengers WHERE cabin IS NOT NULL AND cabin!=''")

rates = {}

rates["tier"] = initialize(["A", "B", "C", "D", "E", "F", "G"])
rates["gender"] = initialize(["male", "female"])
rates["age"] = initialize(["child", "teenager", "young adult", "adult", "senior"])
rates["isAlone"] = initialize(["true", "false"])
rates["class"] = initialize([1, 2, 3])
rates["port"] = initialize(["Q", "S", "C"])

passengers = select_query("SELECT * FROM DefaultPassengers")

for passenger in passengers:
    # Cabin
    cabins = passenger["cabin"].split()
    for cabin in cabins:
        if cabin[0] in rates["tier"].keys():
            rates["tier"][cabin[0]]["survived"] += passenger["survived"]
            rates["tier"][cabin[0]]["total"] += 1

    # Gender
    rates["gender"][passenger["sex"]]["survived"] += passenger["survived"]
    rates["gender"][passenger["sex"]]["total"] += 1

    # Age
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
    
    rates["age"][age_group]["survived"] += passenger["survived"]
    rates["age"][age_group]["total"] += 1

    # Alone
    rates["isAlone"]["true" if passenger["isAlone"] == 1 else "false"]["survived"] += passenger["survived"]
    rates["isAlone"]["true" if passenger["isAlone"] == 1 else "false"]["total"] += 1

    # Class
    rates["class"][passenger["class"]]["survived"] += passenger["survived"]
    rates["class"][passenger["class"]]["total"] += 1

    # Port
    if passenger["port"] in rates["port"].keys():
        rates["port"][passenger["port"]]["survived"] += passenger["survived"]
        rates["port"][passenger["port"]]["total"] += 1

for category in rates:
    for sub in rates[category]:
        rates[category][sub]["percentage"] = rates[category][sub]["survived"] / rates[category][sub]["total"]

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(rates, f, indent=4)