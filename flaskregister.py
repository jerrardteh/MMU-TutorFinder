from flask import Flask, request, url_for, redirect, render_template, flash
import sqlite3
import hashlib

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def html():
    return render_template('flaskregister.html')

@app.route('/register/successful')
def success():
    return 'Account successfully created!'

@app.route('/register', methods=['POST', 'GET'])
def register():
    fullName = request.form['fullname']
    user = request.form['username']

    rawPassword = request.form['password']
    bytePassword = rawPassword.encode('utf-8')
    hashPassword = hashlib.sha256(bytePassword).hexdigest()

    mmuid = request.form['mmuid']

    email = request.form['email']
    if not email.endswith('mmu.edu.my'):
        flash('Email must be a MMU email address!')
        return redirect('/')
    
    role = request.form['role']
    bio = request.form['bio']
    subjects = request.form['subjects']

    cursor.execute('''INSERT INTO Users (full_name, username, password_hash, mmuid, email, role, bio, subjects) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (fullName, user, hashPassword, mmuid, email, role, bio, subjects)
                   )

    conn.commit()

    return redirect(url_for('success'))



if __name__ == '__main__':
    app.run(debug=True)


cursor.close()
conn.close()