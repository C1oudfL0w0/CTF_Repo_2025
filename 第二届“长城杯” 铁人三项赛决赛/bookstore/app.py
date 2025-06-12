from flask import Flask, request, \
    session, g, redirect, url_for, \
    abort, render_template, flash, \
    render_template_string
import os
# from settings import *
import pickle
import re
import traceback

app = Flask(__name__)
app.config.update(dict(
    DATABASE='',
    DEBUG=True,
    SECRET_KEY="os.environ.get('SECRET_KEY')",
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

class ErrorHandler():
    def __init__(self):
        self.notfound = "Oops! That page doesn't exist."
        self.badreqyest = "Your Rquest We Could Not Understand"

@app.errorhandler(404)
def page_not_found(error):

    template = '''
    <div class="center-content error">
        <h1>{error.notfound} !!!</h1>
        <h2>''' + request.url + '''</h2>
    </div>
    '''
    error = ErrorHandler()
    return template.format(error = error), 404


def get_books(book_name=None):
    if book_name:
        try:
            with open('./books/' + book_name, 'rb') as f:
                book = pickle.load(f)
            return book
        except:
            return None
    else:
        books = []
        dirs = os.listdir("./books/")
        for book_name in dirs:
            try:
                with open('./books/' + book_name, 'rb') as f:
                    book = pickle.load(f)
            except:
                continue
            books.append(book)
        return books


def save_book(book_name, book_bio, book_img, book_price, book_num):
    book = pickle.dumps((book_name, book_img, book_bio, book_price, book_num))
    with open('./books/' + book_name, 'wb') as f:
        f.write(book)
        

@app.route("/bookAdd",methods=['POST','GET'])
def upload():
    if session.get('logged_in', None) and session.get('name', None) == 'admin':
        if request.method == 'POST':
            try:
                book_name = request.form.get('book_name')
                book_bio = request.form.get('book_bio')
                book_price = int(request.form.get('book_price'))
                book_num = int(request.form.get('book_num'))

                f = request.files['myfile']
                book_img = f.filename
                save_book(book_name, book_bio, book_img, book_price, book_num)
                f.save("./static/img/"+f.filename)
            except Exception as e:
                traceback.print_exc()
                return "Something Wrong!!!"
            return "Book Add Success"
        else:
            return render_template('tmpl/bookAdd.html')
    return 'You are not login'

# 主页
@app.route('/')
@app.route('/index')
def index():
    if session.get('logged_in', None):
        name = session.get('name')
        if name == 'admin':
            return render_template('index.html')
    else:
        session['logged_in'] = 0
        session['name'] = 'Anonymous'
        msg = 'Please Login First, {} '

    return render_template('index.html', msg=msg.format(session.get('name')))

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "123456":
            session['logged_in'] = 1
            session['name'] = 'admin'
        msg = 'Please Login First, {} '
        return render_template('index.html', msg=msg.format(session.get('name')))    

@app.route('/logout')
def logout():
    session['logged_in'] = 0
    session['name'] = 'Anonymous'
    msg = 'Please Login First, {} '
    return render_template('index.html', msg=msg.format(session.get('name')))  

@app.route('/bookDetail/<string:book_name>')
def book_detail(book_name):
    book = get_books(book_name)
    return render_template('tmpl/bookDetail.html', book=book)

@app.route('/backup')
def hint():
    return open(__file__).read()

@app.route('/bookList')
def book_list():
    books = get_books()
    return render_template('tmpl/bookList.html', books=books)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False,port=8080)