from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
import logging
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"Application started at {datetime.now().strftime('%I:%M %p +08, %A, %B %d, %Y')}")

# Create a Blueprint for tutor profile-related routes
tutorprofile_bp = Blueprint('tutorprofile', __name__)

# Directory to store uploaded profile pictures
UPLOAD_FOLDER = os.path.abspath(os.path.join('static', 'profilepicture'))

# Allowed image file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp'}

# Maximum allowed file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Helper function to connect to the SQLite database
def get_db():
    db = sqlite3.connect('users.db')
    db.row_factory = sqlite3.Row  # Enable dict-like row access
    return db

# Helper function to check if uploaded file is valid
def allowed_file(filename, file):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and
        (not file.content_length or file.content_length <= MAX_FILE_SIZE)
    )

# Check if selected subject code is valid
def is_valid_subject(subject_code, available_subjects):
    return any(s['code'] == subject_code for s in available_subjects)

# Route to display tutor profile
@tutorprofile_bp.route('/tutorprofile')
def tutor_profile():
    if 'username' not in session:
        return redirect('/flasklogin')  # Require login

    db = get_db()
    # Retrieve user profile data
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, subjects, profile_picture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        return "User not found", 404

    # Validate stored subject
    cursor = db.cursor()
    cursor.execute('SELECT subjectcode FROM subjects')
    valid_subjects = [row[0] for row in cursor.fetchall()]
    subjects = user['subjects'] if user['subjects'] in valid_subjects else ''

    # Render profile template
    return render_template('tutorprofile.html', user={**user, 'subjects': subjects}, os=os, valid_subjects=valid_subjects)

# Route to edit tutor profile
@tutorprofile_bp.route('/editprofile', methods=['GET', 'POST'])
def edit_tutor_profile():
    if 'username' not in session:
        logging.info("User not logged in, redirecting to login")
        return redirect('/flasklogin')

    db = get_db()
    # Retrieve current user info
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, subjects, profile_picture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        logging.error(f"User {session['username']} not found")
        return "User not found", 404

    # Fetch all available subjects for selection
    cursor = db.cursor()
    cursor.execute('SELECT subjectcode, subjectname, semester FROM subjects')
    allsubjects = cursor.fetchall()
    subjects = [{'code': row[0], 'name': row[1], 'semester': row[2]} for row in allsubjects]

    # Get existing price from tutors table (matched by full_name)
    price_row = db.execute('SELECT price FROM tutors WHERE full_name = ?', (user['full_name'],)).fetchone()
    existing_price = str(price_row['price']) if price_row else ''

    if request.method == 'POST':
        # Collect form input with fallback to existing values
        full_name = request.form.get('full_name', '').strip() or user['full_name']
        email = request.form.get('email', '').strip() or user['email']
        mmuid = request.form.get('mmuid', '').strip() or user['mmuid']
        bio = request.form.get('bio', '').strip() or user['bio']
        subject = request.form.get('subject', '').strip()
        price = request.form.get('price', '').strip()

        # Validate subject and price
        if subject and not is_valid_subject(subject, subjects):
            flash("Invalid subject.", "error")
            subject = ''
        if price and not price.isdigit():
            flash("Price must be a number.", "error")
            return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os, price=price)

        price_changed = price != existing_price
        filename = user['profile_picture'] or 'default.png'
        file_uploaded = False

        # Handle profile picture upload
        file = request.files.get('profile_picture')
        if file and file.filename:
            if not allowed_file(file.filename, file):
                flash(f"Invalid file type or size.", 'error')
                return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os, price=price)

            safe_filename = secure_filename(file.filename)
            filename = f"{session['username']}_{safe_filename}"
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(upload_path)
            file_uploaded = True

            # Delete old profile picture if it's not the default
            if user['profile_picture'] and user['profile_picture'] != 'default.png':
                old_path = os.path.join(UPLOAD_FOLDER, user['profile_picture'])
                if os.path.exists(old_path):
                    os.remove(old_path)

        # Check if any data has changed
        has_changes = (
            full_name != user['full_name'] or
            email != user['email'] or
            mmuid != user['mmuid'] or
            bio != user['bio'] or
            subject != user['subjects'] or
            file_uploaded or
            price_changed
        )

        if not has_changes:
            flash("No changes made.", "info")
            return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os, price=price)

        try:
            # Update Users table
            db.execute(
                '''UPDATE Users SET full_name = ?, email = ?, mmuid = ?, bio = ?, subjects = ?, profile_picture = ? WHERE username = ?''',
                (full_name, email, mmuid, bio, subject, filename, session['username'])
            )
            # Update price in tutors table if changed
            if price_changed:
                db.execute(
                    '''UPDATE tutors SET price = ? WHERE full_name = ?''',
                    (int(price), full_name)
                )
            db.commit()
            flash("Profile updated!", "success")
            return redirect(url_for('tutorprofile.tutor_profile'))

        except Exception as e:
            flash(f"Update failed: {e}", "error")
            logging.error(f"Update error: {e}")
            return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os, price=price)

    # For GET requests, render the edit form
    return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os, price=existing_price)
