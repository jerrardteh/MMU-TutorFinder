from flask import Flask, request, url_for, redirect, render_template, flash, Blueprint, config
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename

app = Blueprint('register', __name__)
UPLOAD_FOLDER = os.path.join('static', 'profile_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp'}

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
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

        # 写入数据库
        try:
            cursor.execute('''
                INSERT INTO Users (
                    full_name, username, password_hash, mmuid, email, role, bio, subjects
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, username, hashed_password, mmuid, email, role, bio, subject,))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Email or username already exists.')
            return render_template('flaskregister.html', subjects=subjects)

        flash('Account created successfully!')
        return redirect(url_for('login.html'))  # 假设你有 login 路由

    return render_template('flaskregister.html', subjects=subjects)