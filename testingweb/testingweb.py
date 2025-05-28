from flask import Flask, render_template, request, redirect, url_for, Blueprint, session
import json
import os
import sqlite3

# Establishes connection to database
def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

app = Blueprint('studentview', __name__, template_folder='templates')
app.secret_key = 'your_secret_key'

# Load tutor data
# tutors = [
#     {
#         'name': 'Jonathan P.',
#         'price': 105,
#         'rating': 5.0,
#         'subject': 'english',
#         'time': 'morning',
#         'img': 'jonathan.jpg',
#         'description': 'Experienced English tutor with 10+ years teaching.',
#         'category': 'Language',
#         'intro': 'Hello! I’m Jonathan, passionate about helping you achieve fluency.'
#     },
#     {
#         'name': 'Craig G.',
#         'price': 131,
#         'rating': 4.5,
#         'subject': 'english',
#         'time': 'evening',
#         'img': 'craig.jpg',
#         'description': 'IELTS and TOEFL preparation expert.',
#         'category': 'Language',
#         'intro': 'Let’s make English fun and practical together!'
#     },
#     {
#         'name': 'Alice M.',
#         'price': 45,
#         'rating': 4.8,
#         'subject': 'math',
#         'time': 'afternoon',
#         'img': 'alice.jpg',
#         'description': 'Math tutor focused on algebra and calculus.',
#         'category': 'STEM',
#         'intro': 'I love helping students see how fun math can be!'
#     }
# ]

conn, cursor = get_db_connection()
cursor.execute('SELECT * FROM TUTORS')
alltutors = cursor.fetchall()

tutors = []
i = 0
for row in alltutors:
    onetutor = alltutors[i]
    tutorname = onetutor[1]
    intro = onetutor[2]
    subjects = onetutor[3]
    price = onetutor[4]
    cursor.execute('SELECT id FROM Users WHERE full_name = ?', (tutorname,))
    tutorrow = cursor.fetchone()
    tutorid = str(tutorrow[0])
    cursor.execute('SELECT stars FROM reviews WHERE tutorid = ?', (tutorid,))
    allstars = cursor.fetchall()
    cursor.execute('SELECT stars FROM reviews WHERE tutorid = ?', (tutorid,))
    validstars = cursor.fetchone()
    totalstars = 0
    n = 0
    averagestars = 0
    roundedstars = 0
    if validstars is not None:
        for row in allstars:
            starrow = allstars[n]
            startoadd = starrow[0]
            print(starrow)
            totalstars = totalstars + startoadd
            print(totalstars)
            n = n + 1
        averagestars = totalstars / n
        roundedstars = round(averagestars, 2)
    time = onetutor[6]
    category = onetutor[7]
    jsontutor = {'name' : tutorname, 'price' : price, 'rating' : roundedstars, 'subject' : subjects, 'time' : time, 'category' : category, 'intro' : intro}
    tutors.append(jsontutor)
    i = i + 1


@app.route('/')
def tutorlist():
    return render_template('testingweb.html', tutors=tutors)

REVIEWS_FILE = os.path.join(os.path.dirname(__file__), 'reviews.json')

@app.route('/reviews')
def reviews():
    tutor_name = request.args.get('name', '')
    reviews_data = {}

    cursor.execute('SELECT ID FROM USERS WHERE FULL_NAME = ?', (tutor_name,))
    tutor = cursor.fetchone()
    tutorid = str(tutor[0])

    cursor.execute('SELECT * FROM REVIEWS WHERE TUTORID = ?', (tutorid,))
    review = cursor.fetchall()

    tutor_reviews = []
    i = 0
    for row in review:
        reviews = review[i]
        studentid = reviews[0]
        cursor.execute('SELECT FULL_NAME FROM USERS WHERE ID = ?', (studentid,))
        name = cursor.fetchone()
        fullname = name[0]

        comment = reviews[2]
        star = reviews[3]
        jsonreview = {'user' : fullname, 'rating' : star, 'comment' : comment}
        tutor_reviews.append(jsonreview)
        i = i + 1

    return render_template('reviews.html', tutor_name=tutor_name, reviews=tutor_reviews)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    tutor_name = request.form['tutor_name']
    user = session.get('username')
    rating = int(request.form['rating'])
    comment = request.form['comment']

    # Fetches student's database id
    cursor.execute('SELECT id FROM USERS WHERE username = ?', (user,))
    validId = cursor.fetchone()
    id = validId[0]
    studentid = str(id)
    print(studentid)
    
    # Fetches tutor's database id
    cursor.execute('SELECT id FROM USERS WHERE FULL_NAME = ?', (tutor_name,))
    validId = cursor.fetchone()
    id = validId[0]
    tutorid = str(id)
    print(tutorid)
    
    # Writes the review into the database 
    cursor.execute('''INSERT INTO REVIEWS (studentid, tutorid, comment, stars) VALUES (?, ?, ?, ?)''', 
                   (studentid, tutorid, comment, rating)
                   )
    
    # Commits the changes
    conn.commit()

    # Load existing reviews
    reviews_data = {}
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as file:
            reviews_data = json.load(file)

    return redirect(url_for('studentview.reviews', name=tutor_name))

@app.route('/timetable')
def studenttimetable():
    studentusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (studentusername,))
    studentrow = cursor.fetchone()
    studentid = studentrow[0]

    i = 0
    classes = []
    cursor.execute('SELECT * FROM tutortimetable WHERE studentid = ?', (studentid,))
    alltutors = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE studentid = ?', (studentid,))
    validtutors = cursor.fetchone()

    if validtutors is None:
        return render_template('studenttimetable.html', classes=classes)
    elif alltutors is not None:
        for row in alltutors:
            lesson = alltutors[i]
            tutorid = lesson[2]
            time = lesson[1]
            day = lesson[0]

            accepted = lesson[4]
            if accepted == 0:
                acceptedmessage = 'Pending acceptance from tutor'
            elif accepted == 1:
                acceptedmessage = 'Tutor has accepted your class'
            else:
                acceptedmessage = 'Acceptance status unknown'

            cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (tutorid,))
            tutorrow = cursor.fetchone()
            tutorname = tutorrow[0]
            cursor.execute('SELECT subjects FROM tutors WHERE id = ?', (tutorid,))
            subjectrow = cursor.fetchone()
            subject = subjectrow[0]
            jsontutor = {'tutorname' : tutorname, 'time' : time, 'day' : day, 'subject' : subject, 'acceptance' : acceptedmessage}
            classes.append(jsontutor)
            i = i + 1

    return render_template('studenttimetable.html', classes=classes)



if __name__ == '__main__':
    app.run(debug=True)
    