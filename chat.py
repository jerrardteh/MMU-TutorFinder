import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify
import os
from flask import redirect, url_for


chat_bp = Blueprint('chat', __name__)

# 初始化数据库表
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ChatMessages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT CHECK(type IN ('text', 'image', 'file', 'video')) NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 加载聊天记录
def load_history(sender, receiver):
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM ChatMessages
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    ''', (sender, receiver, receiver, sender))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 保存消息
def save_message(sender, receiver, content, msg_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ChatMessages (sender, receiver, content, type, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (sender, receiver, content, msg_type, timestamp))
    conn.commit()
    conn.close()

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat_route():
    sender = session.get('username')
    receiver = request.args.get('receiver')

    if not sender or not receiver:
        return jsonify({"error": "Sender and receiver are required"}), 400

    if request.method == 'GET':
        messages = load_history(sender, receiver)
        return render_template('chat.html', sender=sender, receiver=receiver, messages=messages)

    if request.method == 'POST':
        content = request.form.get('message')
        msg_type = 'text'

        if 'video' in request.files and request.files['video']:
            video_file = request.files['video']
            video_path = f"static/videos/{video_file.filename}"
            video_file.save(video_path)
            content = video_path
            msg_type = 'video'

        elif 'image' in request.files and request.files['image']:
            image_file = request.files['image']
            image_path = f"static/images/{image_file.filename}"
            image_file.save(image_path)
            content = image_path
            msg_type = 'image'

        elif 'file' in request.files and request.files['file']:
            file = request.files['file']
            file_path = f"static/files/{file.filename}"
            file.save(file_path)
            content = file_path
            msg_type = 'file'

        if not content:
            return jsonify({'error': 'Message content is required'}), 400

        save_message(sender, receiver, content, msg_type)

        # ✅ 改成页面重定向
        return redirect(url_for('chat.chat_route', sender=sender, receiver=receiver))