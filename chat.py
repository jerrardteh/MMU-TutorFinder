# Required imports
import sqlite3
import os
import uuid
from datetime import datetime
from flask import Blueprint, redirect, render_template, request, session, jsonify, url_for

# Create a Flask Blueprint for the chat system
chat_bp = Blueprint('chat', __name__)

# Path to the SQLite database
DB_PATH = 'users.db'

# Initialize the database and create the ChatMessages table if it doesn't exist
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

# Establish a database connection with row factory for dictionary-like access
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Load the chat history between two users (sender and receiver), ordered by timestamp
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
    return [dict(row) for row in rows]  # Convert rows to list of dictionaries

# Save a chat message (text, image, file, or video) to the database
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

# Save an uploaded file (image, video, or general file) with a unique name to the correct folder
def save_file(file, folder):
    file_ext = file.filename.rsplit('.', 1)[-1]  # Get file extension
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"  # Create unique filename
    relative_path = os.path.join(folder, unique_filename)
    full_path = os.path.join('static', relative_path)  # Full static path
    os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Create directory if it doesn't exist
    file.save(full_path)
    return relative_path  # Return the relative path to be saved in DB

# Initialize the chat table when the module is loaded
init_db()

# Route to handle chat between users
@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat_route():
    # Get the sender from the session and receiver from query string
    sender = session.get('username')
    receiver = request.args.get('receiver')

    # Both sender and receiver are required
    if not sender or not receiver:
        return jsonify({"error": "Sender and receiver are required"}), 400

    # Handle GET request: display the chat page with message history
    if request.method == 'GET':
        messages = load_history(sender, receiver)
        return render_template('chat.html', sender=sender, receiver=receiver, messages=messages)

    # Handle POST request: send a message
    content = request.form.get('message')
    msg_type = 'text'  # Default message type

    # If a video is uploaded
    if 'video' in request.files and request.files['video']:
        video_file = request.files['video']
        content = save_file(video_file, 'videos')
        msg_type = 'video'

    # If an image is uploaded
    elif 'image' in request.files and request.files['image']:
        image_file = request.files['image']
        content = save_file(image_file, 'images')
        msg_type = 'image'

    # If a file is uploaded
    elif 'file' in request.files and request.files['file']:
        file = request.files['file']
        content = save_file(file, 'files')
        msg_type = 'file'

    # If no content was provided
    if not content:
        return jsonify({'error': 'Message content is required'}), 400

    # Save the message to the database
    save_message(sender, receiver, content, msg_type)

    # Redirect to the same chat route to reload the chat history
    return redirect(url_for('chat.chat_route', sender=sender, receiver=receiver))
