from flask import Flask, render_template, request, redirect, url_for, Blueprint
import json
import os
import sqlite3

# Establish connection to database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

app = Blueprint('studentview', __name__, template_folder='templates')

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
    star = onetutor[5]
    time = onetutor[6]
    category = onetutor[7]
    jsontutor = {'name' : tutorname, 'price' : price, 'rating' : star, 'subject' : subjects, 'time' : time, 'category' : category, 'intro' : intro}
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
    user = request.form['user']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    # Fetches student's database id
    cursor.execute('SELECT id FROM USERS WHERE FULL_NAME = ?', (user,))
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
if __name__ == '__main__':
    app.run(debug=True)
