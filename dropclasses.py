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
        dropname = request.form['dropname']
        time = request.form['droptime']
        day = request.form['dropday']
        freeid = '0'

        conn, cursor = get_db_connection()
        cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
        idrow = cursor.fetchone()
        id = idrow[0]

        cursor.execute('SELECT id FROM Users WHERE full_name = ?', (dropname,))
        droprow = cursor.fetchone()
        dropid = droprow[0]

        cursor.execute('SELECT role FROM Users WHERE username = ?', (username,))
        rolerow = cursor.fetchone()
        role = rolerow[0]

        if role == 'student':
            cursor.execute('UPDATE tutortimetable SET accepted = ? WHERE tutorid = ? AND day = ? AND time = ? AND studentid = ?', (freeid, dropid, day, time, id,))
            cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE tutorid = ? AND day = ? AND time = ? AND studentid = ?', (freeid, dropid, day, time, id,))
            conn.commit()
            return redirect(url_for('studentview.studenttimetable'))
        if role == 'tutor':
            cursor.execute('UPDATE tutortimetable SET accepted = ? WHERE tutorid = ? AND day = ? AND time = ? AND studentid = ?', (freeid, id, day, time, dropid,))
            cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE tutorid = ? AND day = ? AND time = ? AND studentid = ?', (freeid, id, day, time, dropid,))
            conn.commit()
            return redirect(url_for('tutorview.tutortimetable'))