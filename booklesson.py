from flask import Flask, session, Blueprint, render_template, request, redirect, url_for
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

app = Blueprint('booklesson', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

@app.route('/submit', methods=['POST', 'GET'])
def booklesson():
    studentusername = session.get('username')
    tutorname = request.form['tutorname']

    conn, cursor = get_db_connection()
    
    cursor.execute('SELECT id FROM Users WHERE username = ?', (studentusername,))
    studentrow = cursor.fetchone()
    studentid = studentrow[0]

    cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    time = request.form['time']

    cursor.execute('''INSERT INTO TUTORSSTUDENT (studentid, tutorid, time) VALUES(?, ?, ?)''',
                (studentid, tutorid, time,)
                )
    conn.commit()
    return redirect(url_for('studentview.tutorlist'))
    


if __name__ == '__main__':
    app.run(debug=True)

    
    