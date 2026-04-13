import csv
from db import insert_query, general_query, select_query

with open('titanic1.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    next(reader)
    for row in reader:
        insert_query("DefaultPassengers", {
            "id": row[0],
            "survived": row[1],
            "class": row[2],
            "sex": "female" if row[3] == "1" else "male",
            "age": row[4],
            "fare": row[10],
            "isAlone": row[9],
        })

with open('titanic2.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    next(reader)
    for row in reader:
        general_query("UPDATE DefaultPassengers SET name=?, cabin=?, port=? WHERE id=?",
            (row[3], row[10], row[11], row[0]))
