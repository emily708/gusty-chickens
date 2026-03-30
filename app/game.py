from flask import Flask, render_template, request, flash, redirect, session

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.get('/start')
def start_get():
    return "example"
