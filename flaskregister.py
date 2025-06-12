from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename

register_bp = Blueprint('register', __name__)
UPLOAD_FOLDER = os.path.join('static', 'profile_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp'}

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    conn, cursor = get_db_connection()

    # 获取 subjects 列表供选择
    cursor.execute('SELECT * FROM subjects')
    allsubjects = cursor.fetchall()
    subjects = [{'code': row[0], 'name': row[1], 'semester': row[2]} for row in allsubjects]

    if request.method == 'POST':
        full_name = request.form['fullname']
        username = request.form['username']
        raw_password = request.form['password']
        mmuid = request.form['mmuid']
        email = request.form['email']
        role = request.form['role']
        bio = request.form['bio']
        subject = request.form['subject']
        picture = request.files.get('profilepic')

        # 验证学号长度
        if len(mmuid) != 10:
            flash('MMUID must be exactly 10 characters!')
            return render_template('flaskregister.html', subjects=subjects)

        # 验证邮箱格式
        if not email.endswith('mmu.edu.my'):
            flash('Email must end with mmu.edu.my')
            return render_template('flaskregister.html', subjects=subjects)

        # 密码加密
        hashed_password = hashlib.sha256(raw_password.encode('utf-8')).hexdigest()

        # 图片处理
        profile_pic_filename = 'default.jpg'
        if picture and picture.filename:
            if allowed_file(picture.filename):
                ext = picture.filename.rsplit('.', 1)[1].lower()
                base_name = secure_filename(picture.filename.rsplit('.', 1)[0])
                profile_pic_filename = f"{username}_{base_name}.{ext}"
                save_path = os.path.join(UPLOAD_FOLDER, profile_pic_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                picture.save(save_path)
            else:
                flash('Invalid image format!')
                return render_template('flaskregister.html', subjects=subjects)

        # 写入数据库
        try:
            cursor.execute('''
                INSERT INTO Users (
                    full_name, username, password_hash, mmuid, email, role, bio, subjects, profile_picture
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, username, hashed_password, mmuid, email, role, bio, subject, profile_pic_filename))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Email or username already exists.')
            return render_template('flaskregister.html', subjects=subjects)

        flash('Account created successfully!')
        return redirect(url_for('login.html'))  # 假设你有 login 路由

    return render_template('flaskregister.html', subjects=subjects)