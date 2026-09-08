import os
import pickle
import base64
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, make_response, request as flask_request, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# 用户类定义
class User:
    def __init__(self, user_id, username, is_admin):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin
        self.logged_in = True

    def serialize(self):
        serialized = pickle.dumps(self)
        hex_encoded = serialized.hex()
        return hex_encoded

    @staticmethod
    def deserialize(hex_encoded):
        try:
            serialized = bytes.fromhex(hex_encoded)
            return pickle.loads(serialized)
        except Exception:
            return None

app = Flask(__name__,
    static_folder='static',
    static_url_path='/banbanbannonono'
)
app.secret_key = os.urandom(24)

# 数据库配置
DATABASE = './blog.db'

@app.context_processor
def inject_variables():
    user = get_current_user()
    return {
        'current_year': datetime.now().year,
        'is_admin': user.is_admin if user else False,
        'username': user.username if user else ''
    }

def get_current_user():
    user_hex = flask_request.cookies.get('Token')
    if user_hex:
        user = User.deserialize(user_hex)
        if user and user.logged_in:
            return user
    return None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        
        cursor = db.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone() is None:
            db.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                ('admin', generate_password_hash('aZPkAfnkXTm6UZKYPvhMWhRxnZENBRfB'), 1)
            )
            db.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                ('guest', generate_password_hash('guest'), 0)
            )
            db.commit()

def login_required(f):
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('请先登录')
            return redirect(url_for('login'))
        elif not user.is_admin:
            flash('您没有权限执行此操作，需要管理员权限')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    # 从数据库获取所有文章
    posts = db.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title and content:
            # 将文章添加到数据库
            db = get_db()
            
            # 查找最小的可用ID（填补已删除的ID空缺）
            cursor = db.execute('''
                SELECT t1.id + 1 AS next_id 
                FROM posts t1 
                LEFT JOIN posts t2 ON t1.id + 1 = t2.id 
                WHERE t2.id IS NULL 
                ORDER BY t1.id 
                LIMIT 1
            ''')
            next_id = cursor.fetchone()
            
            # 如果没有空缺的ID，使用最大的现有ID+1
            if not next_id:
                cursor = db.execute('SELECT MAX(id) FROM posts')
                max_id = cursor.fetchone()[0]
                next_id = max_id + 1 if max_id else 1
            else:
                next_id = next_id['next_id']
            
            # 使用找到的ID插入新文章
            db.execute(
                'INSERT INTO posts (id, title, content) VALUES (?, ?, ?)',
                (next_id, title, content)
            )
            db.commit()
            flash('文章添加成功！')
            return redirect(url_for('index'))
        else:
            flash('标题和内容不能为空！')
    return render_template('add_post.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post:
        return render_template('view_post.html', post=post, post_id=post_id)
    else:
        flash('文章不存在！')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['is_admin'] == 1)
            user_hex = user_obj.serialize()
            response = make_response(redirect(url_for('index')))
            response.set_cookie('Token', user_hex, max_age=86400, httponly=True, secure=False)
            flash('登录成功！')
            return response
        else:
            flash('用户名或密码错误！')
    return render_template('login.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    response.set_cookie('Token', '', expires=0)
    flash('已成功登出！')
    return response

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post:
        db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        db.commit()
        flash('文章已成功删除！')
    else:
        flash('文章不存在！')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run("0.0.0.0", port=5000)
