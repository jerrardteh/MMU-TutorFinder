from flask import Blueprint, render_template, session, redirect, request, url_for, flash
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Directory to save uploaded transcripts
UPLOAD_FOLDER = r"static\transcripts"
# Allowed file types for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'webp'}

# Define Blueprint for tutor view
tutorview = Blueprint('tutorview', __name__)
DB_PATH = 'users.db'

# Function to connect to database with row factory
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Function to connect to database with cursor
def db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

# Check if uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Save uploaded file with a unique name
def save_file(file, folder):
    file_ext = file.filename.rsplit('.', 1)[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    relative_path = os.path.join(folder, unique_filename)
    full_path = os.path.join('static', relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    file.save(full_path)
    return relative_path

# Save a chat message to the database
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

# Route to view students and their messages
@tutorview.route('/', methods=['GET'])
def getstudents():
    tutorusername = session.get('username')
    if not tutorusername:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get tutor ID
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    if not tutorrow:
        conn.close()
        return 'No tutor found!'
    tutorid = tutorrow['id']

    # Get students linked to this tutor with lesson times
    cursor.execute('SELECT studentid, time FROM tutortimetable WHERE tutorid = ?', (tutorid,))
    bound_students = cursor.fetchall()

    lessons_dict = {}

    for student in bound_students:
        studentid = student['studentid']
        time = student['time'] or 'No lesson'

        cursor.execute('SELECT full_name, username FROM Users WHERE ID = ?', (studentid,))
        studentrow = cursor.fetchone()
        if not studentrow:
            continue
        studentname = studentrow['full_name']
        studentusername = studentrow['username']

        lessons_dict[studentusername] = {
            'studentname': studentname,
            'time': time
        }

    # Find students who have chatted with the tutor
    cursor.execute('''
        SELECT DISTINCT sender FROM ChatMessages WHERE receiver = ?
        UNION
        SELECT DISTINCT receiver FROM ChatMessages WHERE sender = ?
    ''', (tutorusername, tutorusername))
    chat_users = cursor.fetchall()

    # Add students from chat history (if not in timetable)
    for row in chat_users:
        username = row[0]
        if username == tutorusername:
            continue
        if username not in lessons_dict:
            cursor.execute('SELECT full_name FROM Users WHERE username = ?', (username,))
            userrow = cursor.fetchone()
            fullname = userrow['full_name'] if userrow else username
            lessons_dict[username] = {
                'studentname': fullname,
                'time': 'No lesson'
            }

    # Load messages for each student
    for studentusername, info in lessons_dict.items():
        cursor.execute('''
            SELECT sender, receiver, content, type, timestamp
            FROM ChatMessages
            WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
            ORDER BY timestamp ASC
        ''', (studentusername, tutorusername, tutorusername, studentusername))
        messages = cursor.fetchall()

        message_list = [
            {
                'sender': m['sender'],
                'receiver': m['receiver'],
                'content': m['content'],
                'type': m['type'],
                'timestamp': m['timestamp']
            } for m in messages
        ]

        lessons_dict[studentusername]['messages'] = message_list

    conn.close()
    lessons = list(lessons_dict.values())

    return render_template('tutorview.html', lessons=lessons)

# Route for sending a message (text, image, video, file)
@tutorview.route('/send_message', methods=['POST'])
def send_message():
    tutorusername = session.get('username')
    if not tutorusername:
        return redirect('/login')

    studentname = request.form.get('studentname')
    if not studentname:
        return redirect(url_for('tutorview.getstudents'))

    content = request.form.get('message')
    msg_type = 'text'

    # Check for file attachments
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
        return redirect(url_for('tutorview.getstudents'))

    save_message(tutorusername, studentname, content, msg_type)

    return redirect(url_for('tutorview.getstudents', selected_student=studentname))

# Route to view tutor’s confirmed timetable
@tutorview.route('/viewtimetable')
def tutortimetable():
    conn, cursor = db_connection()

    tutorusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    i = 0
    classes = []
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0 AND accepted != 0', (tutorid,))
    allstudents = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0 AND accepted != 0', (tutorid,))
    validstudents = cursor.fetchone()

    # Build JSON list of confirmed classes
    if validstudents is None:
        return render_template('tutortimetable.html', classes=classes)
    elif allstudents is not None:
        for row in allstudents:
            lesson = allstudents[i]
            studentid = lesson[3]
            time = lesson[1]
            day = lesson[0]
            cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (studentid,))
            studentrow = cursor.fetchone()
            studentname = studentrow[0]
            jsonstudent = {'studentname': studentname, 'time': time, 'day': day}
            classes.append(jsonstudent)
            i += 1

    return render_template('tutortimetable.html', classes=classes)

# Route to view unaccepted lesson requests
@tutorview.route('/acceptlesson')
def acceptlesson():
    conn, cursor = db_connection()

    tutorusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    unaccepted = '0'
    notstudentid = '0'
    cursor.execute('SELECT * FROM tutortimetable WHERE accepted = ? AND studentid != ? AND tutorid = ?', (unaccepted, notstudentid, tutorid))
    alllessons = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE accepted = ? AND studentid != ? AND tutorid = ?', (unaccepted, notstudentid, tutorid))
    validlessons = cursor.fetchone()

    i = 0
    lessons = []
    if validlessons is None:
        return render_template('acceptlesson.html', lessons=lessons)
    elif alllessons is not None:
        for row in alllessons:
            lesson = alllessons[i]
            day = lesson[0]
            time = lesson[1]
            studentid = lesson[3]
            cursor.execute('SELECT full_name FROM Users WHERE id = ?', (studentid,))
            studentrow = cursor.fetchone()
            studentname = studentrow[0]
            jsonlesson = {'day': day, 'time': time, 'studentname': studentname}
            lessons.append(jsonlesson)
            i += 1

    return render_template('acceptlesson.html', lessons=lessons)

# Route to submit acceptance of a lesson
@tutorview.route('/acceptlesson/submit', methods=['GET', 'POST'])
def submitacceptlesson():
    if request.method == 'POST':
        conn, cursor = db_connection()
        decision = request.form['decision']

        if decision == 'accept':
            day = request.form['day']
            time = request.form['time']
            studentname = request.form['studentname']

            cursor.execute('SELECT id FROM Users WHERE full_name = ?', (studentname,))
            studentrow = cursor.fetchone()
            studentid = studentrow[0]

            acceptedvalue = '1'
            cursor.execute('UPDATE tutortimetable SET accepted = ? WHERE day = ? AND time = ? AND studentid = ?', (acceptedvalue, day, time, studentid,))
            conn.commit()

        elif decision == 'deny':
            day = request.form['day']
            time = request.form['time']
            studentname = request.form['studentname']

            cursor.execute('SELECT id FROM Users WHERE full_name = ?', (studentname,))
            studentrow = cursor.fetchone()
            studentid = studentrow[0]

            denyvalue = '0'
            cursor.execute('UPDATE tutortimetable SET studentid = ? WHERE day = ? AND time = ? AND accepted = ?', (denyvalue, day, time, denyvalue,))
            conn.commit()
            
    return redirect(url_for('tutorview.acceptlesson'))

# Route to view uploaded transcript and decision
@tutorview.route('/transcript/view')
def viewtranscript():
    username = session.get('username')

    conn, cursor = db_connection()
    cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    cursor.execute('SELECT transcriptpath FROM transcripts WHERE tutorid = ?', (tutorid,))
    transcriptrow = cursor.fetchone()
    if transcriptrow is not None:
        transcriptfilename = transcriptrow[0]
        transcriptpath = '/static/transcripts/' + transcriptfilename
    else:
        transcriptpath = 'None'

    # Check transcript decision
    cursor.execute('SELECT accepted FROM transcripts WHERE tutorid = ?', (tutorid,))
    acceptedrow = cursor.fetchone()
    if acceptedrow is not None:
        accepted = acceptedrow[0]
        if accepted == 0:
            decision = 'No decision has been made yet!'
        elif accepted == 1:
            decision = 'Accepted!'
        elif accepted == 2:
            decision = 'Denied!'
        else:
            decision = 'Unknown!'
    else:
        decision = 'You have not uploaded your transcript yet!'

    transcript = [{'transcript': transcriptpath, 'decision': decision}]
    return render_template('viewtranscript.html', transcript=transcript)

# Route to upload a new transcript
@tutorview.route('/transcript/submit', methods=['GET', 'POST'])
def submittranscript():
    if request.method == 'POST':
        transcript = request.files['transcript']
        username = session.get('username')

        if not allowed_file(transcript.filename):
            flash('Invalid File Type!')
            return redirect(url_for('tutorview.viewtranscript'))

        elif transcript:
            conn, cursor = db_connection()
            cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))
            tutorrow = cursor.fetchone()
            tutorid = tutorrow[0]

            # Check if this tutor has uploaded before
            cursor.execute('SELECT transcriptpath FROM transcripts WHERE tutorid = ?', (tutorid,))
            tutorrow = cursor.fetchone()
            if tutorrow is None:
                transcriptnumber = 0
                cursor.execute('INSERT INTO transcripts (tutorid) VALUES (?)', (tutorid,))
            else:
                current = tutorrow[0]
                currentfilename = current.split('.')[0]
                transcriptnumber = int(currentfilename.split('_')[-1])

            # Create new unique filename
            transcriptnumber += 1
            filename = secure_filename(transcript.filename)
            extension = filename.rsplit('.', 1)[-1]
            newfilename = username + "_" + str(transcriptnumber) + "." + extension
            transcript.save(os.path.join(UPLOAD_FOLDER, newfilename))

            accepted = 0
            cursor.execute('UPDATE transcripts SET transcriptpath = ? WHERE tutorid = ?', (newfilename, tutorid,))
            conn.commit()
            cursor.execute('UPDATE transcripts SET accepted = ? WHERE tutorid = ?', (accepted, tutorid,))
            conn.commit()
            flash('Transcript Uploaded Successfully!')

        return render_template('viewtranscript.html')
