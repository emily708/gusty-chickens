from flask import Blueprint, Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.get('/signup')
def signup_get():
    return "example"
