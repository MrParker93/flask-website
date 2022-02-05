from models import Entry
from helpers import login_required
from app import app, db, app_config

from peewee import IntegrityError
from playhouse.flask_utils import get_object_or_404, object_list

from flask import flash, session, request, redirect, render_template, url_for
from werkzeug.security import check_password_hash, generate_password_hash


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():

    next_url = request.args.get('next') or request.form.get('next')

    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')

        if password == app_config['APP']['PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session
            flash('Successfully logged in.', 'success')
            return redirect(next_url or url_for('index'))

        else:
            flash('Incorrect password.', 'danger')

    return render_template('login.html', next_url=next_url)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/')
def index():
    search_query = request.args.get('q')
    if search_query:
        query = Entry.search(search_query)
    else:
        query = Entry.public().order_by(Entry.timestamp.desc())
    return object_list(
        'index.html',
        query,
        search=search_query,
        check_bounds=False
        )

def create_or_edit(entry, template):
    if request.method == 'POST':
        entry.title = request.form.get('title') or ''
        entry.content = request.form.get('content') or ''
        entry.published = request.form.get('published') or False
        if not (entry.title or entry.content):
            flash('Title and content are required.', 'danger')
        else:
            try:
                with db.atomic():
                    entry.save()
            except IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Post succesfully created.', 'success')
                if entry.published:
                    return redirect(url_for('detail', slug=entry.slug))
                else:
                    return redirect(url_for('edit', slug=entry.slug))
    return render_template(template, entry=entry)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return create_or_edit(Entry(title='', content=''), 'create.html')

@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('index.html', query)

@app.route('/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Entry.select()
    else:
        query = Entry.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('detail.html', entry=entry
    )

@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    return create_or_edit(entry, 'edit.html')