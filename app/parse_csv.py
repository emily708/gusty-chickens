import csv
from db import insert_query, general_query, select_query

with open('titanic1.csv', newline='') as titanic_data:
    reader = csv.reader(titanic_data)
    for row in reader:
        insert_query("DefaultPassengers", {
            "id": row[0],
            "survived": row[1],
            "class": row[2],
            "sex": row[3],
            "age": row[4],
            "fare": row[10],
            "isAlone": row[9],
        })
