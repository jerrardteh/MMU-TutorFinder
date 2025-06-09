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

@app.route('/register/successful')
def success():
    return 'Account successfully created!'

@app.route('/register', methods=['POST', 'GET'])
def register():
    conn, cursor = get_db_connection()
    if request.method == 'POST':
        fullName = request.form['fullname']
        user = request.form['username']

        rawPassword = request.form['password']
        bytePassword = rawPassword.encode('utf-8')
        hashPassword = hashlib.sha256(bytePassword).hexdigest()

        mmuid = request.form['mmuid']
        mmuidlength = len(mmuid)
        if mmuidlength != 10:
            flash('Id must have 10 characters!')
            return redirect(url_for('register.html'))

        email = request.form['email']
        if not email.endswith('mmu.edu.my'):
            flash('Email must be a MMU email address!')
            return redirect(url_for('register.html'))
        
        role = request.form['role']
        picture = request.files['profilepic']
        print(allowed_file(picture.filename))
        newfilename = ""
        if picture.filename == "":
            newfilename = 'default.jpg'
        elif allowed_file(picture.filename) == False and newfilename != 'default.jpg':
            flash ("Invalid File Type!")
            return redirect(url_for('register.html'))
        elif picture and allowed_file(picture.filename):
            filename = secure_filename(picture.filename)
            splitfilename = filename.split(".")
            fileextension = splitfilename[-1]
            newfilename = user + "." + fileextension
            picture.save(os.path.join(UPLOAD_FOLDER, newfilename))

        bio = request.form['bio']
        subjects = request.form['subject']

        conn, cursor = get_db_connection()

        cursor.execute('''INSERT INTO Users (full_name, username, password_hash, mmuid, email, role, bio, subjects, profilepicture) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (fullName, user, hashPassword, mmuid, email, role, bio, subjects, newfilename)
                    )

        conn.commit()

        flash('Account Successfully Created!')
        return redirect(url_for('login.html'))
    
    return render_template(url_for('register.html'))



if __name__ == '__main__':
    app.run(debug=True)