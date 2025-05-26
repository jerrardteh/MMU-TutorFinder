import sqlite3
import os
import uuid
from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session, jsonify, url_for

chat_bp = Blueprint('chat', __name__)

DB_PATH = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_history(sender, receiver):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM ChatMessages
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    ''', (sender, receiver, receiver, sender))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_message(sender, receiver, content, msg_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ChatMessages (sender, receiver, content, type, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (sender, receiver, content, msg_type, timestamp))
    conn.commit()
    conn.close()

def save_file(file, folder):
    file_ext = file.filename.rsplit('.', 1)[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    relative_path = os.path.join(folder, unique_filename)
    full_path = os.path.join('static', relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    file.save(full_path)
    return relative_path

init_db()

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat_route():
    sender = session.get('username')
    receiver = request.args.get('receiver')
    if not sender or not receiver:
        return jsonify({"error": "Sender and receiver are required"}), 400

    if request.method == 'GET':
        messages = load_history(sender, receiver)
        return render_template('chat.html', sender=sender, receiver=receiver, messages=messages)

    content = request.form.get('message')
    msg_type = 'text'

    if 'video' in request.files and request.files['video']:
        video_file = request.files['video']
        content = save_file(video_file, 'videos')
        msg_type = 'video'
    elif 'image' in request.files and request.files['image']:
        image_file = request.files['image']
        content = save_file(image_file, 'images')
        msg_type = 'image'
    elif 'file' in request.files and request.files['file']:
        file = request.files['file']
        content = save_file(file, 'files')
        msg_type = 'file'

    if not content:
        return jsonify({'error': 'Message content is required'}), 400

    save_message(sender, receiver, content, msg_type)
    
    return redirect(url_for('chat.chat_route', sender=sender, receiver=receiver))