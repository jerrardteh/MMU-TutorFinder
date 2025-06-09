from flask import Blueprint, render_template, session, g, redirect, request, flash, url_for
import sqlite3

studentprofile_bp = Blueprint('studentprofile', __name__)
DATABASE = 'users.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@studentprofile_bp.teardown_app_request
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()

@studentprofile_bp.route('/studentprofile')
def student_profile():
    if 'username' not in session:
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        return "User not found", 404

    return render_template('studentprofile.html', user=user)

@studentprofile_bp.route('/studentprofile/edit', methods=['GET', 'POST'])
def edit_student_profile():
    if 'username' not in session:
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if request.method == 'POST':
        full_name = request.form.get('full_name').strip()
        email = request.form.get('email').strip()
        mmuid = request.form.get('mmuid').strip()

        if not full_name or not email or not mmuid:
            flash('Please fill in all fields.', 'error')
            return render_template('studentprofile_edit.html', user=user)

        if (full_name == user['full_name'] and
            email == user['email'] and
            mmuid == user['mmuid']):
            flash('No changes detected. Please modify at least one field.', 'error')
            return render_template('studentprofile_edit.html', user=user)

        try:
            db.execute(
                "UPDATE Users SET full_name = ?, email = ?, mmuid = ? WHERE username = ?",
                (full_name, email, mmuid, session['username'])
            )
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('studentprofile.student_profile'))
        except Exception as e:
            flash('Update failed: ' + str(e), 'error')
            return render_template('studentprofile_edit.html', user=user)

    return render_template('studentprofile_edit.html', user=user)
