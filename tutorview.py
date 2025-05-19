from flask import Flask, Blueprint, render_template, session, redirect
import sqlite3


app = Blueprint('tutorview', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

@app.route('/')
def tutorview():
    return(render_template('tutorview.html'))

@app.route('/viewtimetable')
def tutortimetable():
    conn, cursor = get_db_connection()

    tutorusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    i = 0
    classes = []
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0', (tutorid,))
    allstudents = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0', (tutorid,))
    validstudents = cursor.fetchone()

    print(allstudents)
    print(validstudents)

    if validstudents is None:
        return 'No Lessons!'
    elif allstudents is not None:
        for row in allstudents:
            lesson = allstudents[i]
            studentid = lesson[3]
            time = lesson[1]
            day = lesson[0]
            cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (studentid,))
            studentrow = cursor.fetchone()
            studentname = studentrow[0]
            jsonstudent = {'studentname' : studentname, 'time' : time, 'day' : day}
            classes.append(jsonstudent)
            i = i + 1

    return render_template('tutortimetable.html', classes=classes)






if __name__ == '__main__':
    app.run(debug=True)