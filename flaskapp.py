import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)

DB_CONNECTION_PATH = 'home/ubuntu/database.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLite setup
conn = sqlite3.connect(DB_CONNECTION_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL, first_name TEXT DEFAULT "lorem", last_name TEXT DEFAULT "ipsum", address MEDIUMTEXT DEFAULT "2600 Clifton Ave");''')
conn.commit()
conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sign-up')
def signUp():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form.get('address', "2600 Clifton Ave")
    address = address if address != '' else "2600 Clifton Ave"

    if confirm_password != password:
        return render_template('register.html', error="Passwords do not match")

    conn = sqlite3.connect(DB_CONNECTION_PATH)
    c = conn.cursor()
    c.execute("SELECT id from users WHERE  username=?", (username,))
    user_already_exists = c.fetchone()
    if user_already_exists != None:
        return render_template('register.html', error="Username already exists")

    try:
        c.execute("INSERT INTO users (username, password, first_name, last_name, email, address) VALUES (?, ?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email, address))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('profile', username=username))

@app.route('/login', methods=['POST'])
def validateLogin():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_CONNECTION_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if user == None or user[0] != password:
        return render_template('login.html', incorrect_pwd=True)
    else:
        return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DB_CONNECTION_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

@app.route('/upload')
def renderUpload():
    return render_template('upload.html', word_count=None)

@app.route('/upload', methods=["POST"])
def countUpload():
    if 'file' not in request.files:
        return redirect(request.url)
        
    file = request.files['file']
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        with open(filepath, 'r') as f:
            content = f.read()
            word_count = len(content.split())
        
        return render_template('upload.html', word_count=word_count, filename=filename)
    
@app.route('/download/<filename>')
def downloadFile(filename):
    return redirect(url_for('static', filename='uploads/' + filename))

if __name__ == '__main__':
    app.run(debug=True)
