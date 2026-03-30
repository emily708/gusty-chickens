from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)

import auth
app.register_blueprint(auth.bp);

@app.get("/")
def home_get():
    return "Hello"

if __name__ == '__main__':
    app.debug = True;
    app.run();
