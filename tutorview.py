from flask import Blueprint, render_template, session, redirect, request, url_for
import sqlite3
import os
import uuid
from datetime import datetime

tutorview = Blueprint('tutorview', __name__)
DB_PATH = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    return conn, conn.cursor()

def save_file(file, folder):
    file_ext = file.filename.rsplit('.', 1)[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    relative_path = os.path.join(folder, unique_filename)
    full_path = os.path.join('static', relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    file.save(full_path)
    return relative_path

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

@tutorview.route('/', methods=['GET'])
def getstudents():
    tutorusername = session.get('username')
    if not tutorusername:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    if not tutorrow:
        conn.close()
        return 'No tutor found!'

    tutorid = tutorrow['id']

    cursor.execute('SELECT studentid, time FROM TUTORSSTUDENT WHERE tutorid = ?', (tutorid,))
    allstudents = cursor.fetchall()

    lessons_dict = {}

    for student in allstudents:
        studentid = student['studentid']
        time = student['time'] or 'No lesson'

        cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (studentid,))
        studentrow = cursor.fetchone()
        if not studentrow:
            continue

        studentname = studentrow['full_name']

        # 保证一个学生只出现一次，且更新最新time
        if studentname in lessons_dict:
            lessons_dict[studentname]['time'] = time
            continue

        cursor.execute('''
            SELECT sender, receiver, content, type, timestamp
            FROM ChatMessages
            WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
            ORDER BY timestamp ASC
        ''', (studentname, tutorusername, tutorusername, studentname))
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

        lessons_dict[studentname] = {
            'studentname': studentname,
            'time': time,
            'messages': message_list
        }

    conn.close()
    lessons = list(lessons_dict.values())
    return render_template('tutorview.html', lessons=lessons)

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

    # 发送完消息后重定向回聊天页面（带学生名字参数，实现不跳回默认页面）
    return redirect(url_for('tutorview.getstudents', selected_student=studentname))

@tutorview.route('/viewtimetable')
def tutortimetable():
    conn, cursor = db_connection()

    tutorusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    i = 0
    classes = []
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0', (tutorid,))
    allstudents = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE tutorid = ? AND studentid != 0', (tutorid,))
    validstudents = cursor.fetchone()

    if validstudents is None:
        return 'No Lessons!'
    elif allstudents is not None:
        for row in allstudents:
            lesson = allstudents[i]
            studentid = lesson[3]
            time = lesson[1]
            day = lesson[0]
            cursor.execute('SELECT full_name FROM Users WHERE ID = ?', (studentid,))
            studentrow = cursor.fetchone()
            studentname = studentrow[0]
            jsonstudent = {'studentname' : studentname, 'time' : time, 'day' : day}
            classes.append(jsonstudent)
            i = i + 1

    return render_template('tutortimetable.html', classes=classes)

@tutorview.route('/acceptlesson')
def acceptlesson():
    conn, cursor = db_connection()

    tutorusername = session.get('username')
    cursor.execute('SELECT id FROM Users WHERE username = ?', (tutorusername,))
    tutorrow = cursor.fetchone()
    tutorid = tutorrow[0]

    unaccepted = '0'
    notstudentid = '0'
    cursor.execute('SELECT * FROM tutortimetable WHERE accepted = ? AND studentid != ?', (unaccepted, notstudentid))
    alllessons = cursor.fetchall()
    cursor.execute('SELECT * FROM tutortimetable WHERE accepted = ? AND studentid != ?', (unaccepted, notstudentid))
    validlessons = cursor.fetchone()

    i = 0
    lessons = []
    if validlessons is None:
        return 'No lessons to accept!'
    elif alllessons is not None:
        for row in alllessons:
            lesson = alllessons[i]
            # Get day and time information
            day = lesson[0]
            time = lesson[1]

            # Get student name
            studentid = lesson[3]
            cursor.execute('SELECT full_name FROM Users WHERE id = ?', (studentid,))
            studentrow = cursor.fetchone()
            studentname = studentrow[0]

            # Append in json format to pass to html
            jsonlesson = {'day' : day, 'time' : time, 'studentname' : studentname}
            lessons.append(jsonlesson)
            i = i + 1
    
    return render_template('acceptlesson.html', lessons=lessons)

@tutorview.route('/acceptlesson/submit', methods=['GET', 'POST'])
def submitacceptlesson():
    if request.method == 'POST':
        conn, cursor = db_connection()

        # Get day, time and student name to be accepted
        day = request.form['day']
        time = request.form['time']
        studentname = request.form['studentname']\
        
        #Find student's id
        cursor.execute('SELECT id FROM Users WHERE full_name = ?', (studentname,))
        studentrow = cursor.fetchone()
        studentid = studentrow[0]

        # Change the accepted value in database
        acceptedvalue = '1'
        cursor.execute('UPDATE tutortimetable SET accepted = ? WHERE day = ? AND time = ? AND studentid =?', (acceptedvalue, day, time, studentid,))
        conn.commit()
        
    return redirect(url_for('tutorview.acceptlesson'))

