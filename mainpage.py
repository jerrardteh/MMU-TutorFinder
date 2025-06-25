from flask import Flask, render_template, Blueprint

app = Blueprint('mainpage', __name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def html():
    return render_template('mainp.html')