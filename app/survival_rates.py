from db import insert_query, general_query, select_query

# calculating rooms
rooms = select_query("SELECT survived,cabin FROM DefaultPassengers WHERE cabin IS NOT NULL AND cabin!=''");

rates = {}

for letter in ["A", "B", "C", "D", "E", "F", "G"]:
    rates[letter] = {
        "total": 0,
        "survived": 0
    }

for room in rooms:
    room["cabin"] = room["cabin"].split()
    for cabin in room["cabin"]:
        if cabin[0] not in rates:
            continue
        rates[cabin[0]]["survived"] += room["survived"]
        rates[cabin[0]]["total"] += 1

print(rates)
