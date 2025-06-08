from flask import Flask, render_template, redirect, url_for, config
from flasklogin import app as login_bp
from flaskregister import app as register_bp
from testingweb.testingweb import app as studentview_bp
from booklesson import app as booklesson_bp
from tutorview import tutorview  
from chat import chat_bp
from addtime import app as addtime_bp
from dropclasses import app as dropclasses_bp
from adminview import app as adminview_bp

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
app.register_blueprint(tutorview, url_prefix='/tutorview')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(addtime_bp, url_prefix='/addtime')
app.register_blueprint(dropclasses_bp, url_prefix='/dropclasses')
app.register_blueprint(adminview_bp, url_prefix='/adminview')

if __name__ == '__main__':
    app.run(debug=True)



