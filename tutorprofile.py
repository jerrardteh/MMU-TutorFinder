from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
import logging
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging with timestamp
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"Application started at {datetime.now().strftime('%I:%M %p +08, %A, %B %d, %Y')}")

tutorprofile_bp = Blueprint('tutorprofile', __name__)
UPLOAD_FOLDER = os.path.abspath(os.path.join('static', 'profilepicture'))  # Use existing profilepicture folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_db():
    db = sqlite3.connect('users.db')
    db.row_factory = sqlite3.Row
    return db

def allowed_file(filename, file):
    if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        logging.warning(f"File {filename} has invalid extension. Allowed: {ALLOWED_EXTENSIONS}")
        return False
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        logging.warning(f"File {filename} exceeds size limit of 5MB")
        return False
    return True

def is_valid_subject(subject_code, available_subjects):
    return any(s['code'] == subject_code for s in available_subjects)

@tutorprofile_bp.route('/tutorprofile')
def tutor_profile():
    if 'username' not in session:
        logging.info("User not logged in, redirecting to login")
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, subjects, profilepicture AS profile_picture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        logging.error(f"User {session['username']} not found")
        return "User not found", 404

    # Sanitize subjects if invalid
    cursor = db.cursor()
    cursor.execute('SELECT code,name,semester FROM subjects')
    valid_subjects = [row[0] for row in cursor.fetchall()]
    #valid_subjects = [row for row in cursor.fetchall()]
    original_subjects = user['subjects']
    subjects = user['subjects'] if user['subjects'] in valid_subjects else ''
    logging.info(f"Rendering profile for {session['username']}, profile_picture: {user['profile_picture']}, original_subjects: {original_subjects}, sanitized_subjects: {subjects}")
    return render_template('tutorprofile.html', user={**user, 'subjects': subjects}, os=os, valid_subjects=valid_subjects)


@tutorprofile_bp.route('/editprofile', methods=['GET', 'POST'])
def edit_tutor_profile():
    if 'username' not in session:
        logging.info("User not logged in, redirecting to login")
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, subjects, profilepicture AS profile_picture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        logging.error(f"User {session['username']} not found")
        return "User not found", 404

    cursor = db.cursor()
    cursor.execute('SELECT code,name,semester FROM subjects')
    allsubjects = cursor.fetchall()
    subjects = [{'code': row[0], 'name': row[1], 'semester': row[2]} for row in allsubjects]

    if request.method == 'POST':
        # Log form and file data
        logging.info(f"Form data: {request.form}")
        logging.info(f"Files: {request.files}")

        # Get form data, fallback to existing values
        full_name = request.form.get('full_name', '').strip() or user['full_name'] or ''
        email = request.form.get('email', '').strip() or user['email'] or ''
        mmuid = request.form.get('mmuid', '').strip() or user['mmuid'] or ''
        bio = request.form.get('bio', '').strip() or user['bio'] or ''
        #subject = request.form.get('subjects', '').strip() or user['subjects'] or ''
        subject = request.form.get('subject', '').strip()
        
        # Validate subject
        if subject and not is_valid_subject(subject, subjects):
            logging.warning(f"Invalid subject code submitted: {subject}, resetting to empty")
            subject = ''
        logging.info(f"Validated subject: {subject}")

        filename = user['profile_picture'] or 'default.png'

        # Track if a file was uploaded
        file_uploaded = False
        file = request.files.get('profile_picture')
        if file and file.filename:
            logging.info(f"Processing file: {file.filename}, size: {file.content_length} bytes")
            if not allowed_file(file.filename, file):
                flash(f"Invalid file: Must be one of {', '.join(ALLOWED_EXTENSIONS)} and under 5MB", 'error')
                logging.error(f"File validation failed for {file.filename}")
                return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)
            safe_filename = secure_filename(file.filename)
            filename = f"{session['username']}_{safe_filename}"
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if not os.path.exists(UPLOAD_FOLDER):
                    flash("Profile picture folder does not exist.", 'error')
                    logging.error(f"Folder {UPLOAD_FOLDER} does not exist")
                    return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)
                logging.info(f"Saving file to: {os.path.abspath(upload_path)}")
                file.save(upload_path)
                if not os.path.exists(upload_path):
                    flash("File was not saved to the server.", 'error')
                    logging.error(f"File not found after saving: {upload_path}")
                    return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)
                file_uploaded = True
                if user['profile_picture'] and user['profile_picture'] != 'default.png':
                    old_picture_path = os.path.join(UPLOAD_FOLDER, user['profile_picture'])
                    if os.path.exists(old_picture_path):
                        logging.info(f"Removing old picture: {old_picture_path}")
                        os.remove(old_picture_path)
            except Exception as e:
                flash(f"Failed to save file: {str(e)}", 'error')
                logging.error(f"File save failed: {str(e)}")
                return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)

        # Log submitted and current values
        logging.info(f"Submitted: full_name={full_name}, email={email}, mmuid={mmuid}, bio={bio}, subject={subject}, filename={filename}")
        logging.info(f"Current: full_name={user['full_name']}, email={user['email']}, mmuid={user['mmuid']}, bio={user['bio']}, subjects={user['subjects']}, profile_picture={user['profile_picture']}")

        # Check for changes
        has_changes = (full_name != (user['full_name'] or '') or 
                       email != (user['email'] or '') or 
                       mmuid != (user['mmuid'] or '') or 
                       bio != (user['bio'] or '') or 
                       subject != (user['subjects'] or '') or 
                       file_uploaded)
        if not has_changes:
            flash('No changes made to the profile.', 'info')
            logging.info("No profile changes detected")
            return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)

        try:
            logging.info(f"Updating profile for {session['username']} with filename: {filename}, subjects: {subject} at {datetime.now().strftime('%I:%M %p +08')}")
            db.execute(
                '''UPDATE Users SET full_name = ?, email = ?, mmuid = ?, bio = ?, subjects = ?, profilepicture = ? WHERE username = ?''',
                (full_name, email, mmuid, bio, subject, filename, session['username'])
            )
            db.commit()
            flash('Profile updated successfully!', 'success')
            logging.info("Profile updated successfully")
            return redirect(url_for('tutorprofile.tutor_profile'))
        except Exception as e:
            flash('Update failed: ' + str(e), 'error')
            logging.error(f"Database update failed: {str(e)}")
            return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)

    logging.info(f"Rendering edit profile page for {session['username']} at {datetime.now().strftime('%I:%M %p +08')}")
    return render_template('tutorprofile_edit.html', user=user, subjects=subjects, os=os)