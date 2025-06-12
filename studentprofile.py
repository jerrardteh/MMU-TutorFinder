from flask import Blueprint, render_template, session, g, redirect, request, flash, url_for
import sqlite3
import os

studentprofile_bp = Blueprint('studentprofile', __name__)
DATABASE = 'users.db'

# 自动初始化数据库与字段
def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # 检查缺失字段并添加
    columns = {
        'full_name': 'TEXT',
        'email': 'TEXT',
        'mmuid': 'TEXT',
        'bio': 'TEXT',
        'subjects': 'TEXT',
    }
    existing = db.execute("PRAGMA table_info(Users)").fetchall()
    existing_columns = {col[1] for col in existing}
    for col_name, col_type in columns.items():
        if col_name not in existing_columns:
            db.execute(f"ALTER TABLE Users ADD COLUMN {col_name} {col_type}")
    db.commit()
    db.close()

# 每次 app 启动时执行初始化
init_db()

# 数据库连接
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

# 显示学生资料
@studentprofile_bp.route('/studentprofile')
def student_profile():
    if 'username' not in session:
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, subjects, profilepicture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    if not user:
        return "User not found", 404

    return render_template('studentprofile.html', user=user)

# 编辑学生资料
@studentprofile_bp.route('/studentprofile/edit', methods=['GET', 'POST'])
def edit_student_profile():
    if 'username' not in session:
        return redirect('/flasklogin')

    db = get_db()
    user = db.execute(
        "SELECT full_name, email, mmuid, bio, profilepicture FROM Users WHERE username = ?",
        (session['username'],)
    ).fetchone()

    allsubjects = db.execute('SELECT * FROM subjects').fetchall()

    subjects = []
    i = 0
    for row in allsubjects:
        subject = allsubjects[i]
        code = subject[0]
        name = subject[1]
        semester = subject[2]
        jsonsubjects = {'code' : code, 'name' : name, 'semester' : semester}
        subjects.append(jsonsubjects)
        i = i + 1


    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        mmuid = request.form.get('mmuid', '').strip()
        bio = request.form.get('bio', '').strip()
        subject = request.form['subject']
        print(subject)

        # 上传图片
        file = request.files.get('profile_picture')
        print(file)
        print(file.filename)
        if file.filename is not None:
            filename = file.filename
            splitfilename = filename.rsplit('.', 1)
            extension = splitfilename[-1]
            filename = session['username'] + '.' + extension
            upload_path = os.path.join('static/profilepicture', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)

        # 验证
        if not full_name or not email or not mmuid:
            flash('Please fill in required fields.', 'error')
            return render_template('studentprofile_edit.html', user=user)

        try:
            db.execute(
                '''UPDATE Users SET full_name = ?, email = ?, mmuid = ?, bio = ?, subjects = ?, profilepicture = ? WHERE username = ?''',
                (full_name, email, mmuid, bio, subjects, filename, session['username'])
            )
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('studentprofile.student_profile'))
        except Exception as e:
            flash('Update failed: ' + str(e), 'error')
            return render_template('studentprofile_edit.html', user=user)

    return render_template('studentprofile_edit.html', user=user, subjects = subjects)