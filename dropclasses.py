from flask import Flask, session, Blueprint, render_template, request, redirect, url_for
import sqlite3

app = Blueprint('droplesson', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def dropclasses():
    if request.method == 'POST':
        username = session.get('username')
        tutorname = request.form['droptutorname']
        time = request.form['droptime']
        day = request.form['dropday']
        freeid = '0'

        conn, cursor = get_db_connection()
        cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
        studentrow = cursor.fetchone()
        studentid = studentrow[0]

        cursor.execute('SELECT id FROM tutors WHERE full_name = ?', (tutorname,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]

        cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE tutorid = ? AND day = ? AND time = ? AND studentid = ?', (freeid, tutorid, day, time, studentid,))
        conn.commit()

    return redirect(url_for('studentview.studenttimetable'))