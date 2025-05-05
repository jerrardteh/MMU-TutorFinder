from flask import Flask, request, url_for, redirect, render_template, session
import sqlite3
import hashlib

# Setup Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('C:/Users/User/OneDrive/Desktop/python/users.db')
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

# Link HTML file to Flask (login page)
@app.route('/')
def html():
    return render_template('flasklogin.html')  # 注意这里不用templates/

# Route to check validity of user
@app.route('/login', methods=['POST', 'GET'])
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
            return redirect(url_for('invalid_user'))
        else:
            correctHash = userResult['password_hash']
            role = userResult['role']
            
            # If password matches, store username in session and redirect to friends page
            if hashPassword == correctHash:
                session['username'] = user  # Store the username in session
                
                # NEW: Redirect directly to friends list (on chat.py server)
                return redirect('http://localhost:5002')
            else:
                return redirect(url_for('invalid_user'))

    # If the method is GET, render the login form
    return render_template('flasklogin.html')

# Page for unsuccessful login
@app.route('/invalid')
def invalid_user():
    return 'Username or password is incorrect!'

# 之前的 hello_user 不再需要跳转过去了，可以保留，不影响
@app.route('/user/<user>/<role>')
def hello_user(user, role):
    if session.get('username') != user:
        return redirect(url_for('login'))  # Redirect to login if session username does not match
    
    return f'Hello {role.capitalize()} {user}'

if __name__ == '__main__':
    app.run(debug=True)
