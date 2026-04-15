from flask import Flask, render_template, request, flash, redirect, session, url_for

app = Flask(__name__)
app.secret_key = b'thegustiestofchickensmuahahahhhahhaha'


import auth
app.register_blueprint(auth.bp)
import game
app.register_blueprint(game.bp)


@app.before_request
def check_authentification():
    if 'username' not in session.keys() and request.blueprint != 'auth' and request.path != '/' and request.endpoint != "static":
        flash("Please log in to view our website", "danger")
        return redirect(url_for("auth.login_get"))

@app.get("/")
def home_get():
    return render_template('startscreen.html')

@app.get("/load")
def load_get():
    return render_template('load.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
