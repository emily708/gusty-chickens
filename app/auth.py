from flask import Blueprint, Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.get('/signup')
def signup_get():
    return render_template('auth/signup.html')

@bp.post('/signup')
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if len(select_query("SELECT * FROM Users WHERE username=?", [username])) != 0:
        flash('Username already exists.', 'error')
        return redirect(url_for('auth.signup_get'))
    hashed_password = generate_password_hash(password)
    insert_query("profiles", {"username": username, "password": hashed_password})
    flash('Sign up successful! Please log in.', 'success')
    return redirect(url_for('auth.login_get'))

@bp.get('/login')
def login_get():
    return render_template('auth/login.html')

@bp.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    rows = select_query("SELECT * FROM profiles WHERE username=?", [username])
    if len(rows) != 0 and check_password_hash(rows[0]['password'], password):
        session['username'] = username
        return redirect(url_for('lobby_get'))
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('auth.login_get'))

@bp.get("/logout")
def logout_get():
    old_username = session.get("username")
    old_lobby = session.get("room")
    if old_lobby and old_username:
        if old_lobby in lobbies and old_username in lobbies[old_lobby]:
            lobbies[old_lobby].remove(old_username)
    session.clear()
    return redirect(url_for("auth.login_get"))


#update username
@bp.post('/update/username')
def update_username():
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login_get'))
    old_username = session['username']
    new_username = request.form.get('new_username')
    if not new_username:
        flash('New username cannot be empty.', 'error')
        return redirect(url_for('settings_get'))
    if select_query("SELECT * FROM profiles WHERE username=?", [new_username]):
        flash('Username already taken.', 'error')
        return redirect(url_for('settings_get'))
    general_query( "UPDATE profiles SET username=? WHERE username=?;",(new_username, old_username))
    session['username'] = new_username
    flash('Username updated successfully.', 'success')
    return redirect(url_for('settings_get'))

#update password
@bp.post('/update/password')
def update_password():
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login_get'))
    username = session['username']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    row = select_query("SELECT password FROM profiles WHERE username=?", [username])
    if not row or not check_password_hash(row[0]['password'], old_password):
        flash('Old password is incorrect.', 'error')
        return redirect(url_for('settings_get'))
    hashed_password = generate_password_hash(new_password)
    general_query("UPDATE profiles SET password=? WHERE username=?;",(hashed_password, username))
    flash('Password updated successfully.', 'success')
    return redirect(url_for('settings_get'))

@bp.get('/signup')
def signup_get():
    return "example"
