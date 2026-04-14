from flask import Flask, render_template, request, flash, redirect, session, Blueprint

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.get('/map')
def map_get():
    return render_template("map.html")
