from flask import Flask, request, url_for, redirect, render_template
import sqlite3
import hashlib

conn = sqlite3.connect('users.db', check_same_thread=False)

cursor = conn.cursor()

app = Flask(__name__)

@app.route('/')
def html():
    return render_template('flasklogin.html')

@app.route('/user/<user>')
def hello_student(user):
    return 'Hello Student %s' %user

@app.route('/tutor/<user>')
def hello_tutor(user):
    return 'Hello Tutor %s' %user

@app.route('/admin/<user>')
def hello_admin(user):
    return 'Hello Admin %s' %user

@app.route('/user/<user>')
def hello_user(user):
    return 'Hello %s' %user

@app.route('/invalid')
def invalid_user():
    return 'Username or password is incorrect!'

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        rawPassword = request.form['password']
        bytePassword = rawPassword.encode('utf-8')
        hashPassword = hashlib.sha256(bytePassword).hexdigest()
        cursor.execute("SELECT password_hash, role FROM Users WHERE USERNAME = ?", (user,))
        userResult = cursor.fetchone()
        cursor.execute
        if userResult is None:
            return redirect(url_for('invalid_user'))
        else:
            correctHash = userResult[0]
            role = userResult[1]
            lowerRole = role.lower()
            if hashPassword == correctHash:
                if lowerRole == 'student':
                    return redirect(url_for('hello_student', user = user))
                elif lowerRole == 'tutor':
                    return redirect(url_for('hello_tutor', user = user))
                elif lowerRole == 'admin':
                    return redirect(url_for('hello_admin', user = user))
                else:
                    return redirect(url_for('hello_user', user = user))
            else:
                return redirect(url_for('invalid_user'))
    else:
        return redirect(url_for('invalid_user'))


if __name__ == '__main__':
    app.run(debug=True)







cursor.close()
conn.close()