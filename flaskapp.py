from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_CONNECTION_PATH = 'home/ubuntu/database.db'

# SQLite setup
conn = sqlite3.connect(DB_CONNECTION_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL, first_name TEXT DEFAULT "lorem", last_name TEXT DEFAULT "ipsum", address MEDIUMTEXT DEFAULT "2600 Clifton Ave");''')
conn.commit()
conn.close()

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

if __name__ == '__main__':
    app.run(debug=True)
