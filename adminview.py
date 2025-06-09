from flask import Flask, Blueprint, session, render_template, request, redirect, url_for
import sqlite3

# Establishes connection to database
def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

app = Blueprint('adminview', __name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def html():
    return render_template('adminview.html')

@app.route('/addsubjects')
def addsubjects():
    conn, cursor = get_db_connection()

    cursor.execute('SELECT * FROM subjects')
    allsubjects = cursor.fetchall()

    subjects = []
    i = 0

    for row in allsubjects:
        subject = allsubjects[i]
        subjectcode = subject[0]
        subjectname = subject[1]
        semester = subject[2]
        jsonsubject = {'code' : subjectcode, 'name' : subjectname, 'semester' : semester}
        subjects.append(jsonsubject)
        i = i + 1

    return render_template('adminaddsubjects.html', subjects=subjects)

@app.route('/addsubjects/submit', methods=['GET', 'POST'])
def submitaddsubjects():
    if request.method == 'POST':
        conn, cursor = get_db_connection()

        subjectcode = request.form['code']
        subjectname = request.form['name']
        semester = request.form['semester']
        cursor.execute('INSERT INTO subjects (subjectcode, subjectname, semester) VALUES (?, ?, ?)', (subjectcode, subjectname, semester,))
        conn.commit()

    return redirect(url_for('adminview.addsubjects'))