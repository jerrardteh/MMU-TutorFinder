from flask import Flask, request, url_for, redirect, render_template, flash, Blueprint, config
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static\profilepicture'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp' }


app = Blueprint('register', __name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def html():
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

    return render_template('flaskregister.html', subjects=subjects)


@app.route('/register', methods=['POST', 'GET'])
def register():
    conn, cursor = get_db_connection()
    if request.method == 'POST':
        fullName = request.form['fullname']
        user = request.form['username']

        rawPassword = request.form['password']
        bytePassword = rawPassword.encode('utf-8')
        hashPassword = hashlib.sha256(bytePassword).hexdigest()

        bio = request.form['bio']
        selectedsubject = request.form['subject']
        role = request.form['role']
        picture = request.files['profilepic']
        mmuid = request.form['mmuid']
        email = request.form['email']

        # Get all available subjects again
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


        cursor.execute('SELECT exists(SELECT 1 FROM Users WHERE username = ?)', (user,))
        usernamerow = cursor.fetchall()
        usernametuple = usernamerow[0]
        usernameexists= usernametuple[0]
        if usernameexists == 1:
            flash ('Username already exists!')
            return render_template('flaskregister.html', fullname = fullName, user = user, password = rawPassword, bio = bio, subjects = subjects, selectedsubject = selectedsubject, role = role, picture = picture, mmuid = mmuid, email = email)


        mmuidlength = len(mmuid)
        if mmuidlength != 10:
            flash('Id must have 10 characters!')
            return render_template('flaskregister.html', fullname = fullName, user = user, password = rawPassword, bio = bio, subjects = subjects, selectedsubject = selectedsubject, role = role, picture = picture, mmuid = mmuid, email = email)


        if not email.endswith('mmu.edu.my'):
            flash('Email must be a MMU email address!')
            return render_template('flaskregister.html', fullname = fullName, user = user, password = rawPassword, bio = bio, subjects = subjects, selectedsubject = selectedsubject, role = role, picture = picture, mmuid = mmuid, email = email)
        
        cursor.execute('SELECT exists(SELECT 1 FROM Users WHERE mmuid = ? AND role = ?)', (mmuid, role,))
        mmuidrow = cursor.fetchall()
        mmuidtuple = mmuidrow[0]
        mmuidexists= mmuidtuple[0]
        if mmuidexists == 1:
            flash ('MMU ID already exists!')
            return render_template('flaskregister.html', fullname = fullName, user = user, password = rawPassword, bio = bio, subjects = subjects, selectedsubject = selectedsubject, role = role, picture = picture, mmuid = mmuid, email = email)

        newfilename = ""
        if picture.filename == "":
            newfilename = 'default.jpg'
        elif allowed_file(picture.filename) == False and newfilename != 'default.jpg':
            flash ("Invalid File Type!")
            return render_template('flaskregister.html', fullname = fullName, user = user, password = rawPassword, bio = bio, subjects = subjects, selectedsubject = selectedsubject, role = role, picture = picture, mmuid = mmuid, email = email)
        elif picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            splitfilename = filename.rsplit(".", 1)
            fileextension = splitfilename[-1]
            newfilename = user + "." + fileextension
            picture.save(os.path.join(UPLOAD_FOLDER, newfilename))


        conn, cursor = get_db_connection()

        cursor.execute('''INSERT INTO Users (full_name, username, password_hash, mmuid, email, role, bio, subjects, profilepicture) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (fullName, user, hashPassword, mmuid, email, role, bio, selectedsubject, newfilename)
                    )

        conn.commit()

        flash('Account Successfully Created!')
        return redirect(url_for('login.html'))
    
    return render_template(url_for('register.html'))



if __name__ == '__main__':
    app.run(debug=True)
