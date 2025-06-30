from flask import Flask, Blueprint, session, render_template, request, redirect, url_for, flash
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
    # Get existing subjects
    cursor.execute('SELECT * FROM subjects')
    allsubjects = cursor.fetchall()

    subjects = []
    i = 0
    # Put existing subject into list for html
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

        # Get input from html form
        semester = request.form['semester']
        subjectcode = request.form['code']
        subjectname = request.form['name']

        # Check if inputted subject already exists
        cursor.execute('SELECT exists(SELECT 1 FROM subjects WHERE subjectcode = ? AND subjectname = ? AND semester = ?)', (subjectcode, subjectname, semester,))
        subjectrow = cursor.fetchall()
        subjecttuple = subjectrow[0]
        subjectexists = subjecttuple[0]
        if subjectexists == 1:
            flash('Subject already exists!')
            return redirect(url_for('adminview.addsubjects'))
        else:
            cursor.execute('INSERT INTO subjects (subjectcode, subjectname, semester) VALUES (?, ?, ?)', (subjectcode, subjectname, semester,))
            conn.commit()

    return redirect(url_for('adminview.addsubjects'))

@app.route('/transcripts')
def transcripts():
    conn, cursor = get_db_connection()
    # Get unaccepted transcripts
    unaccepted = 0
    cursor.execute('SELECT * from transcripts WHERE accepted = ?', (unaccepted,))
    transcriptrow = cursor.fetchall()
    # Check if there is any transcripts to be accepted
    cursor.execute('SELECT * from transcripts WHERE accepted = ?', (unaccepted,))
    validtranscripts = cursor.fetchone()
    i = 0
    transcripts = []
    if validtranscripts is not None:
        for row in transcriptrow:
            # Puts all unaccepted transcripts into list for html
            transcript = transcriptrow[i]
            tutorid = transcript[0]
            cursor.execute('SELECT full_name FROM Users WHERE id = ?', (tutorid,))
            tutorrow = cursor.fetchone()
            tutorname = tutorrow[0]
            transcriptfilename = transcript[1]
            transcriptpath = '/static/transcripts/' + transcriptfilename
            jsontranscript = {'tutorname' : tutorname, 'transcript' : transcriptpath}
            transcripts.append(jsontranscript)
            i = i + 1
    else:
        # Flash message to user
        flash('No transcripts waiting for approval!')
        return render_template('accepttranscripts.html')
    
    return render_template('accepttranscripts.html', transcripts = transcripts)

@app.route('/transcripts/submit', methods=['GET', 'POST'])
def accepttranscripts():
    if request.method == 'POST':
        conn, cursor = get_db_connection()
        tutorname = request.form['tutorname']
        decision = request.form['decision']
        cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
        tutorrow = cursor.fetchone()
        if tutorrow is not None:
            # Get tutor id
            tutorid = tutorrow[0]
            # Initialise value for accepted and denied
            accepted = 1
            denied = 2
            # If accepted, change value in database. If denied, don't change anything in database
            if decision == 'accept':
                cursor.execute('UPDATE transcripts SET accepted = ? WHERE tutorid = ?', (accepted, tutorid,))
                conn.commit()
                message = tutorname + "'s transcript has been approved!"
            elif decision == 'deny':
                cursor.execute('UPDATE transcripts SET accepted = ? WHERE tutorid = ?', (denied, tutorid,))
                conn.commit()
                message = tutorname + "'s transcript has been denied!"
            else:
                message = "Approval or denial request has failed! Try again!"

            # Flash message to user
            flash(message)
            return redirect(url_for('adminview.transcripts'))