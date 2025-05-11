from flask import Flask, render_template, session
from flasklogin import app as login
from flaskregister import app as register
from testingweb.testingweb import app as studentview
from booklesson import app as booklesson
from tutorview import app as tutorview

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def appfunc():
    return render_template('main.html')

app.register_blueprint(login, url_prefix = '/login')
app.register_blueprint(studentview, url_prefix = '/studentview')
app.register_blueprint(register, url_prefix = '/register')
app.register_blueprint(booklesson, url_prefix = '/booklesson')
app.register_blueprint(tutorview, url_prefix = '/tutorview')



if __name__ == '__main__':
    app.run(debug=True)
