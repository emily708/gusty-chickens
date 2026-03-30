from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)

import auth
app.register_blueprint(auth.bp);

@app.before_request
def check_authentification():
    if 'username' not in session.keys() and request.blueprint != 'auth' and request.path != '/':
        flash("Please log in to view our website", "danger")
        return redirect(url_for("auth.login_get"))

@app.get("/")
def home_get():
    return "Hello"

if __name__ == '__main__':
    app.debug = True;
    app.run();
