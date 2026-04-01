from flask import Flask, render_template, request, flash, redirect, session, url_for

app = Flask(__name__)
app.secret_key = b'thegustiestofchickensmuahahahhhahhaha'


import auth
app.register_blueprint(auth.bp)

@app.before_request
def check_authentification():
    if 'username' not in session.keys() and request.blueprint != 'auth' and request.path != '/':
        flash("Please log in to view our website", "danger")
        return redirect(url_for("auth.login_get"))

@app.get("/")
def home_get():
    return render_template('startscreen.html')

@app.get("/login")
def login():
    return render_template('login.html')
    if loggedin():
        return render_template('load.html')

    if request.method == 'POST':
        session.clear()
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                rows = c.execute("SELECT * FROM player WHERE username = ?;", (request.form['username'],))
                result = rows.fetchone()

                if result is None:
                    return render_template("login.html", t="Username does not exist")
                elif (request.form['password'] != result[1]):
                    return render_template("login.html", t="Your password was incorrect")

                session['username'] = request.form['username'].lower()

                return render_template('load.html')
    else:
        return render_template("login.html")

@app.get("/register")
def register():
    return render_template("register.html")
    if loggedin():
        return render_template('load.html')
    else:
        if request.method == 'POST':
            with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()

                rows = c.execute("SELECT username FROM player WHERE username = ?", (request.form['username'].lower(),))
                result = rows.fetchone()
                if result:
                    return render_template("register.html", invalid="Duplicate username")
                session.permanent = True

                # for invalid requests / empty form responses
                t = ""
                if(request.form['username'] == "" or request.form['password'] == ""):
                    t = "Please enter a valid "
                    if(request.form['username'] == ""):
                        t = t + "username "
                    if(request.form['password'] == ""):
                        t = t + "password "
                    return render_template("register.html", t)

                session.clear()
                session.permanent = True
                session['username'] = request.form['username'].lower()

                return render_template('load.html')
    return render_template("register.html")

if __name__ == '__main__':
    app.debug = True
    app.run()
