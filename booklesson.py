from flask import Flask, session, Blueprint, render_template, request, redirect, url_for
import sqlite3

app = Blueprint('booklesson', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn, conn.cursor()

@app.route('/')
def html():
    conn, cursor = get_db_connection()
    tutorname = request.args.get('tutor')
    
    # Get tutor id
    cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    #Search for available lessons for tutor
    studentid = '0'
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid = ?', (tutorid, studentid))
    availablelessons = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid = ?', (tutorid, studentid))
    validlessons = cursor.fetchone()


    if validlessons is None:
        return('No Lessons!')
    else:
        lessons = []
        i = 0
        
        for row in availablelessons:
            lesson = availablelessons[i]
            day = lesson[0]
            time = lesson[1]
            daytime = day + ' ' + time
            jsonlessons = {'daytime' : daytime}
            lessons.append(jsonlessons)
            i = i + 1

        return render_template('booklesson.html', lesson=lessons, tutorname=tutorname)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = session.get('username')

        conn, cursor = get_db_connection()

        tutorname = request.form['tutorname']
        cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
        tutorrow = cursor.fetchone()
        tutorid = tutorrow[0]

        cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
        studentrow = cursor.fetchone()
        studentid = studentrow[0]

        daytime = request.form['daytime']
        splitdaytime = daytime.split(" ")
        day = splitdaytime[0]
        time = splitdaytime[1]
        
        cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE tutorid = ? AND day = ? AND time = ?', (studentid, tutorid, day, time,))
        conn.commit()

    return redirect(url_for('studentview.tutorlist'))
    


if __name__ == '__main__':
    app.run(debug=True)

    
    