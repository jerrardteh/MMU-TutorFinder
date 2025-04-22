from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configure upload folder and chat history folder
UPLOAD_FOLDER = 'static/uploads'
CHAT_HISTORY_FOLDER = 'chat_history'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHAT_HISTORY_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt'}

# Check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load chat history from file
def load_history(sender, receiver):
    filename = get_chat_filename(sender, receiver)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Save chat history to file
def save_history(sender, receiver, messages):
    filename = get_chat_filename(sender, receiver)
    for msg in messages:
        msg['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp to each message
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# Generate a consistent chat filename regardless of sender/receiver order
def get_chat_filename(sender, receiver):
    chat_file = '_'.join(sorted([sender, receiver])) + '_chat.json'
    return os.path.join(CHAT_HISTORY_FOLDER, chat_file)

# Route for the chat interface
@app.route('/chat/<sender>/<receiver>', methods=['GET', 'POST'])
def chat(sender, receiver):
    if request.method == 'POST':
        msg_type = 'text'
        content = request.form.get('message', '')

        # Handle file upload
        if 'file' in request.files and allowed_file(request.files['file'].filename):
            file = request.files['file']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            content = filename
            ext = filename.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                msg_type = 'image'
            else:
                msg_type = 'file'

        # Load current chat history
        messages = load_history(sender, receiver)

        # Add new message
        messages.append({
            'sender': sender,
            'receiver': receiver,
            'content': content,
            'type': msg_type
        })

        # Save to JSON file
        save_history(sender, receiver, messages)

    # Load all chat history
    messages = load_history(sender, receiver)
    return render_template("chat.html", sender=sender, receiver=receiver, messages=messages)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
