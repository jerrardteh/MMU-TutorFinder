from flask import Flask, session, Blueprint, render_template, request, redirect, url_for
import sqlite3
import os

app = Blueprint('booklesson', __name__)
app.secret_key = 'your_secret_key'

DATABASE = os.path.join(os.path.dirname(__file__), 'users.db')


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            full_name TEXT,
            password_hash TEXT
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tutortimetable (
            day TEXT,
            time TEXT,
            tutorid INTEGER,
            studentid INTEGER
        )
    ''')

    
    # cursor.execute("SELECT COUNT(*) FROM Users")
    # if cursor.fetchone()[0] == 0:
    #     cursor.execute("INSERT INTO Users (username, full_name, password_hash) VALUES (?, ?, ?)", ("tutor1", "John Doe", "hashed_tutor"))
    #     cursor.execute("INSERT INTO Users (username, full_name, password_hash) VALUES (?, ?, ?)", ("student1", "Jane Smith", "hashed_student"))

    #     cursor.execute("SELECT id FROM Users WHERE full_name = ?", ("John Doe",))
    #     tutorid = cursor.fetchone()[0]

    #     sample_times = [("Monday", "10:00"), ("Wednesday", "14:00"), ("Friday", "09:00")]
    #     for day, time in sample_times:
    #         cursor.execute("INSERT INTO tutortimetable (day, time, tutorid, studentid) VALUES (?, ?, ?, ?)", (day, time, tutorid, 0))

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    return conn, conn.cursor()

init_db()

@app.route('/')
def html():
    conn, cursor = get_db_connection()
    tutorname = request.args.get('tutor')

    if not tutorname:
        return "Tutor not specified."

    cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
    tutorrow = cursor.fetchone()
    if not tutorrow:
        return f"Tutor '{tutorname}' not found."
    
    tutorid = tutorrow[0]
    # Get the tutor's available lesson
    studentid = '0'
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid = ?', (tutorid, studentid))
    availablelessons = cursor.fetchall()
    # Puts all available lessons into list for html
    lessons = []
    for lesson in availablelessons:
        day, time = lesson[0], lesson[1]
        lessons.append({'daytime': f"{day} {time}"})

    return render_template('booklesson.html', lesson=lessons, tutorname=tutorname)

# Route for booking lesson
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = session.get('username')
        if not username:
            return "You must be logged in."

        conn, cursor = get_db_connection()
        # Get tutor id
        tutorname = request.form['tutorname']
        cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
        tutorrow = cursor.fetchone()
        if not tutorrow:
            return "Tutor not found."
        tutorid = tutorrow[0]
        # Get student id
        cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
        studentrow = cursor.fetchone()
        if not studentrow:
            return "Student not found."
        studentid = studentrow[0]

        daytime = request.form['daytime']
        day, time = daytime.split(" ")
        
        cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE tutorid = ? AND day = ? AND time = ?', (studentid, tutorid, day, time))
        conn.commit()

    return redirect(url_for('studentview.tutorlist'))


if __name__ == '__main__':
    flask_app = Flask(__name__)
    flask_app.register_blueprint(app, url_prefix='/booklesson')
    flask_app.secret_key = 'your_secret_key'
    flask_app.run(debug=True)
