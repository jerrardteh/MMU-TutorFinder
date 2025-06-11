from flask import Flask, request, url_for, redirect, render_template, session, Blueprint, flash
import sqlite3
import hashlib

# Setup Flask app
app = Blueprint('login', __name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn

# Link HTML file to Flask (login page)
@app.route('/')
def html():
    return render_template('flasklogin.html')  # No need to include 'templates/' in the path

# Route to check validity of user
@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        rawPassword = request.form['password']
        bytePassword = rawPassword.encode('utf-8')
        hashPassword = hashlib.sha256(bytePassword).hexdigest()

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the hashed password and role from the database
        cursor.execute("SELECT password_hash, role FROM Users WHERE username = ?", (user,))
        userResult = cursor.fetchone()

        # If the user doesn't exist, redirect to invalid page
        if userResult is None:
            return redirect('invalid')
        else:
            correctHash = userResult['password_hash']
            role = userResult['role']
            
            # If password matches, store username in session and redirect to friends page
            if hashPassword == correctHash:
                session['username'] = user
                if role == 'student':
                    return redirect(url_for('studentview.tutorlist'))
                elif role == 'tutor':
                    return redirect(url_for('tutorview.getstudents'))
                elif role == 'admin':
                    return redirect(url_for('adminview.html'))
            else:
                return redirect('invalid')

    # If the method is GET, render the login form
    return render_template('flasklogin.html')

# Page for unsuccessful login
@app.route('/invalid')
def invalid_user():
    flash('Incorrect username or password!')
    return render_template('flasklogin.html')


if __name__ == '__main__':
    app.run(debug=True)
