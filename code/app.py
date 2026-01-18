import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='../UI', static_folder='../static')
app.config['SECRET_KEY'] = 'your-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Создание базы данных
with app.app_context():
    db.create_all()

# --- Маршруты (Routes) ---

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], avatar=session.get('avatar', ''))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['avatar'] = user.avatar
            return redirect(url_for('index'))
        flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует')
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/search_users')
def search_users():
    query = request.args.get('q', '')
    users = User.query.filter(User.username.contains(query)).limit(10).all()
    return {"users": [{"id": u.id, "username": u.username, "avatar": u.avatar} for u in users if u.id != session.get('user_id')]}

# --- Socket.IO логика ---

@socketio.on('connect')
def on_connect():
    if 'user_id' in session:
        join_room(f"user_{session['user_id']}")
        print(f"User {session['username']} connected to room user_{session['user_id']}")

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = session.get('user_id')
    recipient_id = data.get('to_id')
    text = data.get('message')

    if sender_id and recipient_id and text:
        # Сохраняем в БД
        msg = Message(sender_id=sender_id, recipient_id=recipient_id, text=text)
        db.session.add(msg)
        db.session.commit()

        # Отправляем получателю
        emit('receive_message', {
            'message': text,
            'from_id': sender_id,
            'from_username': session['username']
        }, room=f"user_{recipient_id}")
        
        # Отправляем самому себе (чтобы отобразилось в чате)
        emit('receive_message', {
            'message': text,
            'from_id': sender_id,
            'from_username': session['username']
        }, room=f"user_{sender_id}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5555, debug=True)