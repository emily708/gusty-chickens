from flask import Flask, render_template, request, flash, redirect, session, Blueprint
from db import select_query, insert_query, general_query

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.get('/start')
def start_get():
    insert_query("Games", {
        "username": session["username"],
        "currLocation": "Compass Platform"
    })
    passengers = select_query("SELECT * FROM DefaultPassengers")
    for passenger in passengers:
        insert_query("Passengers", {
            
        })
    return redirect("/map")

@bp.get('/map')
def map_get():
    game = select_query("SELECT * FROM Games WHERE active=TRUE AND username=?", session["username"])
    return render_template("map.html")
