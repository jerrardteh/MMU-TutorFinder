from flask import Flask, render_template, Blueprint, request, session, url_for, redirect, flash
import sqlite3

app = Blueprint('addtime', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

conn, cursor = get_db_connection()

@app.route('/')
def html():
    username = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ?', (tutorid,))
    daytimerow = cursor.fetchall()
    i = 0
    daytime = []

    for row in daytimerow:
        dayntime = daytimerow[i]
        day = dayntime[0]
        time = dayntime[1]
        jsondaytime = {'day' : day, 'time' : time}
        daytime.append(jsondaytime)
        i = i + 1
    
    return(render_template('addtime.html', daytime=daytime))

@app.route('/submit', methods=['POST', 'GET'])
def addtime():
    if request.method == 'POST':
        username = session.get('username')
        day = request.form['day']
        time = request.form['time']

        cursor.execute('SELECT id FROM Users WHERE USERNAME = ?', (username,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]
        studentid = '0'
        
        cursor.execute('SELECT * FROM tutortimetable WHERE day = ? AND time = ? AND tutorid = ?', (day, time, tutorid))
        existing = cursor.fetchone()
        if existing is None:
            cursor.execute('INSERT INTO tutortimetable (tutorid, day, time, studentid) VALUES (?, ?, ?, ?)', (tutorid, day, time, studentid))
            conn.commit()
        else:
            flash('You already have a class at this time!')
            return redirect(url_for('addtime.addtime'))
        
    return(redirect('/addtime'))


if __name__ == '__main__':
    app.run(debug=True)