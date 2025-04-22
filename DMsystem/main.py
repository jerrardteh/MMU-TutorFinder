from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 模拟用户和消息（保存在内存中）
users = {}
messages = []  # (sender, receiver, content)

@app.route('/')
def index():
    return redirect(url_for('chat'))

@app.route('/chat.html', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        content = request.form.get('message')

        if sender and receiver and content:
            messages.append((sender, receiver, content))

    return render_template('chat.html', users=users.keys(), messages=messages)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    if username and username not in users:
        users[username] = []
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
