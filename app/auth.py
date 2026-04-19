from flask import Blueprint, Flask, render_template, request, flash, redirect, session, url_for
from db import *
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.get('/register')
def register_get():
    return render_template('auth/register.html')

@bp.post('/register')
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if len(select_query("SELECT * FROM Users WHERE username=?", [username])) != 0:
        flash('Username already exists.', 'error')
        return redirect(url_for('auth.register_get'))
    hashed_password = generate_password_hash(password)
    insert_query("Users", {"username": username, "password": hashed_password})
    flash('Sign up successful! Please log in.', 'success')
    return redirect(url_for('auth.login_get'))

@bp.get('/login')
def login_get():
    return render_template('auth/login.html')

@bp.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    rows = select_query("SELECT * FROM Users WHERE username=?", [username])
    if len(rows) != 0 and check_password_hash(rows[0]['password'], password):
        session['username'] = username
        return redirect(url_for('load_get'))
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('auth.login_get'))

@bp.get("/logout")
def logout_get():
    # Clears game on log out
    general_query("UPDATE Games SET active=FALSE WHERE username=?", [session["username"]])
    session.clear()
    return redirect(url_for("auth.login_get"))
