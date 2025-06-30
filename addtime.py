from flask import Flask, render_template, Blueprint, request, session, url_for, redirect, flash
import sqlite3

app = Blueprint('addtime', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

conn, cursor = get_db_connection()

# Route for tutors to add time 
@app.route('/')
def html():
    # Get tutor ID
    username = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]
    # Get existing day and time based on tutorid
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ?', (tutorid,))
    daytimerow = cursor.fetchall()
    i = 0
    daytime = []
    # Puts all existing day and time into list for html
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
        # Get tutor ID
        cursor.execute('SELECT id FROM Users WHERE USERNAME = ?', (username,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]
        studentid = '0'
        accepted = '0'
        # Check if day and time already exists
        cursor.execute('SELECT * FROM tutortimetable WHERE day = ? AND time = ? AND tutorid = ?', (day, time, tutorid))
        existing = cursor.fetchone()
        if existing is None:
            cursor.execute('INSERT INTO tutortimetable (tutorid, day, time, studentid, accepted) VALUES (?, ?, ?, ?, ?)', (tutorid, day, time, studentid, accepted,))
            conn.commit()
        else:
            flash('You already have a class at this time!')
            return redirect(url_for('addtime.addtime'))
        
    return redirect(url_for('addtime.html'))
# Route for tutor to remove their day and time
@app.route('/droptime/submit', methods=['POST', 'GET'])
def droptime():
    if request.method == 'POST':
        username = session.get('username')
        day = request.form['day']
        time = request.form['time']
        # Get tutor id
        cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]
        # Deletes the day and time from database based on tutorid
        cursor.execute('DELETE FROM tutortimetable WHERE day = ? AND time = ? AND tutorid = ?', (day, time, tutorid,))
        conn.commit()

        return redirect(url_for('addtime.html'))
    
    return redirect(url_for('addtime.html'))


if __name__ == '__main__':
    app.run(debug=True)