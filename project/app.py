import sqlite3
from flask import Flask, g, render_template, flash, redirect, url_for, request, session

# App configuration
DATABASE = 'flaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'change'

# Create and initialize a new Flask app
app = Flask(__name__)

# Load the app configuration
app.config.from_object(__name__)

# Connect to database
def connect_db():
    """Database connected."""
    db_connection = sqlite3.connect(app.config['DATABASE'])
    db_connection.row_factory = sqlite3.Row
    return db_connection

# Create and initialize database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as sql_file:
            db.cursor().executescript(sql_file.read())
        db.commit()

# Open database connection
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# Close current database connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/')
def index():
    db = get_db()
    db_cursor = db.execute('SELECT * FROM entries ORDER BY id DESC')
    db_entries = db_cursor.fetchall()
    return render_template('index.html', db_entries=db_entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/sessions management"""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Successfully logged in!')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """User logout/authentication/session management"""
    session.pop('logged_in', None)
    flash('Successfully logged out!')
    return redirect(url_for('index'))
    
@app.route('/add', methods=['POST'])
def add_entry():
    """Add new post to the database"""
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO entries (title, text) VALUES (?, ?)',
            [request.form['title'], request.form['text']]
        )
        db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
