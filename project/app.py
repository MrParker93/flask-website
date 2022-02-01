import os
import re
import urllib
import datetime
import functools

from flask import (Flask, Response, flash, session, request,
                    redirect, render_template, url_for, Markup)

from micawber.cache import Cache as OEmbedCache
from micawber import  bootstrap_basic, parse_html

from markdown import markdown
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.codehilite import  CodeHiliteExtension

from peewee import *
from playhouse.sqlite_ext import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list

# Configurations for app
ADMIN_PASSWORD = 'admin'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')
DEBUG = False
SECRET_KEY = 'dev'

# Initialize app
app = Flask(__name__)

# Get app configuration from this file
app.config.from_object(__name__)

# Integrate peewee database with Flask app database
flask_db = FlaskDB(app)
database = flask_db.database

# Enables embedding of supported providers such as: YouTube, Vimeo etc
oembed_providers = bootstrap_basic(OEmbedCache())


# Handles blog entries 
class Entry(flask_db.Model):
    title = CharField()
    slug = CharField(unique=True)  # URL safe version of blog title
    content = TextField()
    published = BooleanField(index=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)

    # Handles displaying published blog posts
    @classmethod
    def public(cls):
        return Entry.select().where(Entry.published == True)

    # Handles searching
    @classmethod
    def search(cls, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return empty query search
            return Entry.select().where(Entry.id == 0)
        else:
            search = ' '.join(words)
        return (Entry
                .select(Entry, FTSEntry.rank().alias('score'))
                .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
                .where(
                    (Entry.published == True) &
                    (FTSEntry.match(search)))
                .order_by(SQL('score')))
    
    # Handles displaying drafted blog posts
    @classmethod
    def drafts(cls):
        return Entry.select().where(Entry.published == False)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Example: title: 'Blog Title', slug: blog-title'
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
        re_entry = super(Entry, self).save(*args, **kwargs)

        # Store in search content
        self.update_search_index()
        return re_entry

    # Adds new entry to full text search table
    def update_search_index(self):
        search_content = '\n'.join((self.title, self.content))
        try:
            fts_entry = FTSEntry.get(FTSEntry.docid == self.id)
        except FTSEntry.DoesNotExist:
            FTSEntry.create(docid=self.id, content=search_content)
        else:
            fts_entry.content = search_content
            fts_entry.save()

    # Converts markdown format into HTML and media objects into embedded objects
    @property
    def html_content(self):
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oember_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH']
        )
        return Markup(oember_content)


# Handles search database
class FTSEntry(FTSModel):
    content = SearchField()

    
    class Meta:
        database = database

# Decorator 
def login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():

    next_url = request.args.get('next') or request.form.get('next')

    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')

        if password == app.config['ADMIN_PASSWORD']:
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
    return object_list('index.html', query, search=search_query)

@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('index.html', query)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry = Entry.create(
                title=request.form['title'],
                content=request.form['content'],
                published=request.form.get('published') or False
            )
            flash('Post submitted.', 'success')
            if entry.published:
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))
        else:
            flash('Title and content are required.', 'danger')
    return render_template('create.html')

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
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry.title = request.form['title']
            entry.content = request.form['content']
            entry.published = request.form.get('published') or False
            entry.save()

            flash('Post has been edited.', 'success')
            if entry.published:
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))
        else:
            flash('Title and content are required.', 'danger')
    return render_template('edit.html')
            
# Helper functions

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(err):
    return Response('<h3>Not found</h3>'), 404

def main():
    database.create_tables([Entry, FTSEntry])
    app.run(debug=True)


if __name__ == '__main__':
    main()