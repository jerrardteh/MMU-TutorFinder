from flask import Flask, render_template, request, redirect, url_for, Blueprint, session
import os
import sqlite3

# 创建 Blueprint
app = Blueprint('studentview', __name__, template_folder='templates')
app.secret_key = 'your_secret_key'

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

# ✅ tutor 动态构建函数
def get_all_tutors():
    conn, cursor = get_db_connection()
    cursor.execute('SELECT * FROM TUTORS')
    alltutors = cursor.fetchall()

    tutors = []
    for onetutor in alltutors:
        tutorid = onetutor[0]
        tutorname = onetutor[1]
        
        cursor.execute('SELECT bio FROM Users WHERE id = ?', (tutorid,))
        biorow = cursor.fetchone()
        intro = biorow[0] if biorow else ''

        cursor.execute('SELECT subjects FROM Users WHERE id = ?', (tutorid,))
        subjectsrow = cursor.fetchone()
        subjects = subjectsrow[0] if subjectsrow else ''

        price = onetutor[3]

        cursor.execute('SELECT stars FROM reviews WHERE tutorid = ?', (str(tutorid),))
        allstars = cursor.fetchall()
        if allstars:
            totalstars = sum([s[0] for s in allstars])
            roundedstar = round(totalstars / len(allstars), 2)
        else:
            roundedstar = 'No reviews yet!'

        picturerow = cursor.execute('SELECT profile_picture FROM Users WHERE id = ?', (tutorid,)).fetchone()
        picture = picturerow[0] if picturerow else 'default.jpg'
        picturepath = '/static/profilepicture/' + picture

        jsontutor = {
            'name': tutorname,
            'price': price,
            'subject': subjects,
            'intro': intro,
            'img': picturepath,
            'rating': roundedstar
        }
        tutors.append(jsontutor)
    
    return tutors

@app.route('/')
def tutorlist():
    tutors = get_all_tutors()
    return render_template('testingweb.html', tutors=tutors)

@app.route('/reviews')
def reviews():
    tutor_name = request.args.get('name', '')
    conn, cursor = get_db_connection()

    cursor.execute('SELECT ID FROM USERS WHERE FULL_NAME = ?', (tutor_name,))
    tutor = cursor.fetchone()
    if not tutor:
        return "Tutor not found", 404
    tutorid = str(tutor[0])

    cursor.execute('SELECT * FROM REVIEWS WHERE TUTORID = ?', (tutorid,))
    review = cursor.fetchall()

    tutor_reviews = []
    for reviews in review:
        studentid = reviews[0]
        cursor.execute('SELECT FULL_NAME FROM USERS WHERE ID = ?', (studentid,))
        name = cursor.fetchone()
        fullname = name[0] if name else 'Unknown'
        comment = reviews[2]
        star = reviews[3]
        jsonreview = {'user': fullname, 'rating': star, 'comment': comment}
        tutor_reviews.append(jsonreview)

    return render_template('reviews.html', tutor_name=tutor_name, reviews=tutor_reviews)

@app.route('/submit_review', methods=['GET', 'POST'])
def submit_review():
    if request.method == 'POST':
        tutor_name = request.form['tutor_name']
        user = session.get('username')
        rating = int(request.form['rating'])
        comment = request.form['comment']

        conn, cursor = get_db_connection()

        # 获取 student ID
        cursor.execute('SELECT id FROM USERS WHERE username = ?', (user,))
        validId = cursor.fetchone()
        studentid = str(validId[0])

        # 获取 tutor ID
        cursor.execute('SELECT id FROM USERS WHERE FULL_NAME = ?', (tutor_name,))
        validId = cursor.fetchone()
        tutorid = str(validId[0])

        # 插入评论
        cursor.execute('''
            INSERT INTO REVIEWS (studentid, tutorid, comment, stars)
            VALUES (?, ?, ?, ?)''',
            (studentid, tutorid, comment, rating)
        )
        conn.commit()

        return redirect(url_for('studentview.reviews', name=tutor_name))

@app.route('/timetable')
def studenttimetable():
    studentusername = session.get('username')
    conn, cursor = get_db_connection()
    cursor.execute('SELECT id FROM Users WHERE username = ?', (studentusername,))
    studentrow = cursor.fetchone()
    studentid = studentrow[0] if studentrow else None

    if not studentid:
        return "Student not found", 404

    cursor.execute('SELECT * FROM tutortimetable WHERE studentid = ?', (studentid,))
    alltutors = cursor.fetchall()

    classes = []
    for lesson in alltutors:
        tutorid = lesson[2]
        time = lesson[1]
        day = lesson[0]
        accepted = lesson[4]
        acceptedmessage = 'Pending acceptance from tutor' if accepted == 0 else (
            'Tutor has accepted your class' if accepted == 1 else 'Acceptance status unknown'
        )

        cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (tutorid,))
        tutorrow = cursor.fetchone()
        tutorname = tutorrow[0] if tutorrow else 'Unknown'

        cursor.execute('SELECT subjects FROM tutors WHERE id = ?', (tutorid,))
        subjectrow = cursor.fetchone()
        subjectcode = subjectrow[0] if subjectrow else '??'

        cursor.execute('SELECT subjectname FROM subjects WHERE subjectcode = ?', (subjectcode,))
        subjectname_row = cursor.fetchone()
        subjectname = subjectname_row[0] if subjectname_row else 'Unknown'

        subject = f'{subjectcode} {subjectname}'
        jsontutor = {
            'tutorname': tutorname,
            'time': time,
            'day': day,
            'subject': subject,
            'acceptance': acceptedmessage
        }
        classes.append(jsontutor)

    return render_template('studenttimetable.html', classes=classes)
