from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Load tutor data
tutors = [
    {
        'name': 'Jonathan P.',
        'price': 105,
        'rating': 5.0,
        'subject': 'english',
        'time': 'morning',
        'img': 'jonathan.jpg',
        'description': 'Experienced English tutor with 10+ years teaching.',
        'category': 'Language',
        'intro': 'Hello! I’m Jonathan, passionate about helping you achieve fluency.'
    },
    {
        'name': 'Craig G.',
        'price': 131,
        'rating': 4.5,
        'subject': 'english',
        'time': 'evening',
        'img': 'craig.jpg',
        'description': 'IELTS and TOEFL preparation expert.',
        'category': 'Language',
        'intro': 'Let’s make English fun and practical together!'
    },
    {
        'name': 'Alice M.',
        'price': 45,
        'rating': 4.8,
        'subject': 'math',
        'time': 'afternoon',
        'img': 'alice.jpg',
        'description': 'Math tutor focused on algebra and calculus.',
        'category': 'STEM',
        'intro': 'I love helping students see how fun math can be!'
    }
]

@app.route('/')
def index():
    return render_template('testingweb.html', tutors=tutors)

REVIEWS_FILE = os.path.join(os.path.dirname(__file__), 'reviews.json')

@app.route('/reviews')
def reviews():
    tutor_name = request.args.get('name', '')
    reviews_data = {}

    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as file:
            reviews_data = json.load(file)

    tutor_reviews = reviews_data.get(tutor_name, [])
    return render_template('reviews.html', tutor_name=tutor_name, reviews=tutor_reviews)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    tutor_name = request.form['tutor_name']
    user = request.form['user']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    new_review = {
        "user": user,
        "rating": rating,
        "comment": comment
    }

    # Load existing reviews
    reviews_data = {}
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE, 'r') as file:
            reviews_data = json.load(file)

    # Add new review
    if tutor_name not in reviews_data:
        reviews_data[tutor_name] = []

    reviews_data[tutor_name].append(new_review)

    # Save back to file
    with open(REVIEWS_FILE, 'w') as file:
        json.dump(reviews_data, file, indent=2)

    return redirect(url_for('reviews', name=tutor_name))
if __name__ == '__main__':
    app.run(debug=True)
