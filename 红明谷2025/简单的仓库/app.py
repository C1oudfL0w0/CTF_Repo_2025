import shutil

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='guest')
    balance = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, username, password, permission="guest"):
        self.username = username
        self.password = password
        self.permission = permission
        self.balance = 0

@app.before_first_request
def create_tables():
    if os.path.exists('warehouse'):
        shutil.rmtree('warehouse')
    os.makedirs('warehouse/admin')
    with open('warehouse/admin/readme.txt', 'w', encoding='utf-8') as f:
        f.write('/var/tmp/flag.txt')

    if os.path.exists('warehouse.db'):
        os.remove('warehouse.db')
    db.create_all()

    user = User(username="admin", password="NeverLoginMe!hhh", permission="admin")
    db.session.add(user)
    db.session.commit()

def validate_input(text):
    return bool(re.match('^[a-zA-Z0-9]{4,10}$', text))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not validate_input(username) or not validate_input(password):
            return render_template('register.html', error='用户名和密码必须是4-10位的字母数字组合')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='用户名已存在')
        
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        
        user_dir = os.path.join('warehouse', username)
        os.makedirs(user_dir)
        with open(os.path.join(user_dir, '使用小仓库开通vip请联系admin充值.txt'), 'w', encoding='utf-8') as f:
            f.write('欢迎使用小仓库')
        with open(os.path.join(user_dir, 'readme.txt'), 'w', encoding='utf-8') as f:
            f.write('欢迎使用小仓库')

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not validate_input(username) or not validate_input(password):
            return render_template('login.html', error='用户名和密码必须是4-10位的字母数字组合')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = username
            return redirect(url_for('warehouse'))
        
        return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/warehouse')
def warehouse():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('login'))

    return render_template('warehouse.html', 
                         username=user.username,
                         permission=user.permission,
                         balance=user.balance)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return '权限不足', 403

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if user.permission not in ['vip', 'admin']:
        session.clear()
        return redirect(url_for('login', error="错误，你不是vip"))
    
    if 'file' not in request.files:
        return redirect(url_for('warehouse'))
    path = request.args.get('path', session['user'])

    if path != user.username:
        return '权限不足，只有管理员能对其他用户的仓库进行上传或下载', 403

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('warehouse'))
    
    filename = secure_filename(file.filename)
    file.save(os.path.join('warehouse', path, filename))
    return redirect(url_for('warehouse'))

@app.route('/download/<filename>')
def download(filename):
    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if user.permission not in ['vip', 'admin']:
        session.clear()
        return '权限错误或不足', 403

    target_user = request.args.get('user', session['user'])
    
    return send_from_directory(os.path.join('warehouse', target_user), filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/files', methods=['POST'])
def get_files():
    if 'user' not in session:
        return {'error': '权限不足'}, 403

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if user.permission not in ['guest', 'vip', 'admin']:
        session.clear()
        return {'error': '权限错误'}, 403
    
    data = request.get_json()
    target_user = data.get('path', session['user'])
    
    base_dir = os.path.join('warehouse', target_user)
    if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
        return {'error': '目录不存在'}, 404
    
    files = os.listdir(base_dir)
    return {'files': files}

@app.route('/api/recharge', methods=['POST'])
def recharge():
    if 'user' not in session:
        return {'error': '未登录'}, 403

    data = request.get_json()
    amount = data.get('amount')
    target_user = data.get('username')
    user_permission = data.get('permission')

    if not amount or not amount.isdigit() or int(amount) <= 0:
        return {'error': '充值金额无效'}, 400

    amount = int(amount)
    user = User.query.filter_by(username=target_user).first()
    if not user:
        return {'error': '用户不存在'}, 404

    if user_permission not in ['guest', 'vip', 'admin']:
        return {'error': '拒绝访问'}, 403

    if user_permission == 'admin':
        user.balance += amount
        db.session.commit()
        return {'message': f'充值成功，当前余额: {user.balance}'}
    else:
        return {'message': '充值请求已提交，等待管理员审核'}

@app.route('/api/upgrade', methods=['POST'])
def upgrade_to_vip():
    if 'user' not in session:
        return {'error': '未登录'}, 403

    user = User.query.filter_by(username=session['user']).first()
    if not user:
        return {'error': '用户不存在'}, 404

    if user.balance < 99999:
        return {'error': '余额不足，无法开通VIP'}, 400

    user.balance -= 99999
    user.permission = 'vip'
    db.session.commit()
    session['permission'] = 'vip'
    return {'message': 'VIP开通成功！'}

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)

