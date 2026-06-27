from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import pickle, time, sys, re
from chikawa import CHIKAWA
import unicodedata

from flask import send_from_directory
app = Flask(__name__)
sys.modules['__main__'].CHIKAWA = CHIKAWA
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATABASE'] = 'database.db'
app.config['ALLOWED_EXTENSIONS'] = {'pkl'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def prepare(node: str) -> str:
    if node is None:
        return None
    node = unicodedata.normalize("NFKC", node)
    node = node.lower()
    node = node.strip()
    return node

def init_db():
    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                upload_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()
init_db()
def get_db():
    return sqlite3.connect(app.config['DATABASE'])
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
@app.route('/')
def index():
    return redirect(url_for('login'))
def waf(data):
    waf_patterns = [
        r'/\*.*\*/',
        r'(?i)(and|or|\&\&|\|\|)',
        r'[\s\+\-\*\/]',
        r'union|select|from|where',
        r';|--|#',
    ]
    for pattern in waf_patterns:
        if re.search(pattern, data):
            return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        name = prepare(username)
        if name != "admin" and name != "Admin" and name != "ᴬdmin":
            flash("only admin can login")
            return redirect(request.url)

        if waf(username) or waf(password):
            flash('Invalid input detected')
            return redirect(request.url)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('panel'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        if username == "admin" or username == "Admin":
            flash("no access, try bypass")
            return redirect(request.url)
        
        name = prepare(username)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (name, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Username already exists')
    return render_template('register.html')
@app.route('/panel')
@login_required
def panel():
    return render_template('panel.html')
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO models (user_id, filename, upload_time)
                VALUES (?, ?, ?)
            ''', (session['user_id'], filename, datetime.now()))
            conn.commit()
            conn.close()
            flash('File uploaded successfully')
            return redirect(url_for('model'))
        else:
            flash('Only .pkl files are allowed')
    return render_template('upload.html')

@app.route('/model')
@login_required
def model():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, filename, upload_time, user_id 
        FROM models 
        ORDER BY upload_time DESC
    ''')
    models = cursor.fetchall()
    conn.close()
    return render_template('model.html', models=models)



@app.route('/execute/<int:model_id>', methods=['POST'])
@login_required
def execute(model_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM models WHERE id = ?', (model_id,))
    file_record = cursor.fetchone()
    conn.close()
    
    if file_record:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record[0])
        if os.path.exists(file_path):
            try:
                model = CHIKAWA.load_model(file_path)
                model_train = CHIKAWA.train(model.data)
                return f"module_name {model.model_name}, {model_train}"
            except Exception as e:
                return f"wrong data {e}"
        else:
            flash('File not found.')
    return redirect(url_for('model'))


@app.route('/download/<int:model_id>', methods=['GET'])
@login_required
def download(model_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM models WHERE id = ?', (model_id,))
    file_record = cursor.fetchone()
    conn.close()

    if file_record:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record[0])
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], file_record[0], as_attachment=True)
        else:
            flash('File not found.')

    return redirect(url_for('model'))

@app.route('/delete/<int:model_id>', methods=['POST'])
@login_required
def delete(model_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM models WHERE id = ? AND user_id = ?',
                    (model_id, session['user_id']))
    file_record = cursor.fetchone()
    if file_record:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record[0])
        if os.path.exists(file_path):
            os.remove(file_path)
        cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
        conn.commit()
    conn.close()
    return redirect(url_for('model'))
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8000)