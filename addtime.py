from flask import Flask, render_template, Blueprint, request, session, url_for, redirect
import sqlite3

app = Blueprint('addtime', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn, conn.cursor()


@app.route('/')
def html():
    return(render_template('addtime.html'))

@app.route('/submit', methods=['POST', 'GET'])
def addtime():
    if request.method == 'POST':
        username = session.get('username')
        day = request.form['day']
        time = request.form['time']

        conn, cursor = get_db_connection()
        cursor.execute('SELECT id FROM Users WHERE USERNAME = ?', (username,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]
        studentid = '0'
        
        cursor.execute('SELECT * FROM tutortimetable WHERE day = ? AND time = ? AND tutorid = ?', (day, time, tutorid))
        existing = cursor.fetchone()
        if existing is None:
            cursor.execute('INSERT INTO tutortimetable (tutorid, day, time, studentid) VALUES (?, ?, ?, ?)', (tutorid, day, time, studentid))
            conn.commit()
        
    return(redirect('/addtime'))


if __name__ == '__main__':
    app.run(debug=True)