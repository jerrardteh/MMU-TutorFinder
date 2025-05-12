from flask import Flask, render_template, redirect, url_for
from flasklogin import app as login_bp
from flaskregister import app as register_bp
from testingweb.testingweb import app as studentview_bp
from booklesson import app as booklesson_bp
from tutorview import app as tutorview_bp
from chat import chat_bp

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define the main route
@app.route('/')
def appfunc():
    return redirect(url_for('login.html'))

# Register Blueprints
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(studentview_bp, url_prefix='/studentview')
app.register_blueprint(register_bp, url_prefix='/register')
app.register_blueprint(booklesson_bp, url_prefix='/booklesson')
app.register_blueprint(tutorview_bp, url_prefix='/tutorview')
app.register_blueprint(chat_bp, url_prefix='/chat')

if __name__ == '__main__':
    app.run(debug=True)
