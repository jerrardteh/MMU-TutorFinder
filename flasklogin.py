from flask import Flask, request, url_for, redirect, render_template
import sqlite3
import hashlib

# Establishes connection to database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)

# Link html file to flask
@app.route('/')
def html():
    return render_template('flasklogin.html')

# Page for successful login as student
@app.route('/user/<user>')
def hello_student(user):
    return 'Hello Student %s' %user

# Page for successful login as tutor
@app.route('/tutor/<user>')
def hello_tutor(user):
    return 'Hello Tutor %s' %user

# Page for successful login as admin
@app.route('/admin/<user>')
def hello_admin(user):
    return 'Hello Admin %s' %user

# Page for successful logn as user (just in case role is not student, tutor or admin but account is valid)
@app.route('/user/<user>')
def hello_user(user):
    return 'Hello %s' %user

#Page for unsuccessful login
@app.route('/invalid')
def invalid_user():
    return 'Username or password is incorrect!'

# Page to check validity of user
@app.route('/login', methods=['POST', 'GET'])
def login():
    user = request.form['username']
    # Hashes the password to compare with stored hashed password in database
    rawPassword = request.form['password']
    bytePassword = rawPassword.encode('utf-8')
    hashPassword = hashlib.sha256(bytePassword).hexdigest()
    # Gets the hashed password and role of user from database
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



if __name__ == '__main__':
    app.run(debug=True)







cursor.close()
conn.close()