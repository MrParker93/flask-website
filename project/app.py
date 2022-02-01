import os
import sqlite3
from pathlib import Path
from functools import wraps
from flask import Flask, Request, g, render_template, flash, redirect, url_for, \
                    request, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy

basedir = Path(__file__).resolve().parent

# App configuration
DATABASE = 'flaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'change'
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{Path(basedir).joinpath(DATABASE)}'
)
SQALCHEMY_TRACK_MODIFICATIONS = False

# Create and initialize a new Flask app
app = Flask(__name__)

# Load the app configuration
app.config.from_object(__name__)

# Initialize sqlalchemy
db = (SQLAlchemy(app))

from project import models

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in.')
            return jsonify({'status': 0, 'message': 'Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function
        
@app.route('/')
def index():
    """Searches database for posts and displays them if exists"""
    db_entries = db.session.query(models.Post)
    return render_template('index.html', db_entries=db_entries)

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

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
    if not session.get('logged_in'):
        abort(401)
    new_post = models.Post(request.form['title'], request.form['text'])
    db.session.add(new_post)
    db.session.commit()
    flash('New post was successfully added')
    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>', methods=['GET'])
@login_required
def delete_entry(post_id):
    """Delete post from the database"""
    result = {'status': 0, 'message': 'Error'}
    try:
        db.session.query(models.Post).filter_by(id=post_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': 'Post deleted.'}
        flash('The post was deleted.')
    except Exception as e:
        result = {'status' : 0, 'message': repr(e)}
    return jsonify(result)

@app.route('/search/', methods=['GET'])
def search():
    query = request.args.get('query')
    entries = db.session.query(models.Post)
    if query:
        return render_template('search.html', entries=entries, query=query)
    return render_template('search.html')


if __name__ == "__main__":
    app.run()