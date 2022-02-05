import re
import datetime
from flask import Markup
from app import app, db, app_config

from micawber.cache import Cache as OEmbedCache
from micawber import  bootstrap_basic, parse_html

from markdown import markdown
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.codehilite import  CodeHiliteExtension

# Enables embedding of supported providers such as: YouTube, Vimeo etc
oembed_providers = bootstrap_basic(OEmbedCache())


# Handles users
class User(db.Model):
    id = db.Column(db.Integer)
    _username = CharField(unique=True, index=True)
    _password = CharField()
    _join_date = DateField(default=datetime.datetime.now)


# Handles blog entries 
class Entry(db.Model):
    _username = ForeignKeyField(User, backref='post')
    _title = CharField()
    _slug = CharField(unique=True)  # URL safe version of blog title
    _content = TextField()
    _published = BooleanField(index=True)
    _timestamp = DateTimeField(default=datetime.datetime.now, index=True)

    # Converts markdown format into HTML and media objects into embedded objects
    @property   
    def html_content(self):
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self._content, extensions=[hilite, extras])
        oember_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app_config['APP']['SITE_WIDTH']
        )
        return Markup(oember_content)

    def save(self, *args, **kwargs):
        if not self._slug:
            # Example: title: 'Blog Title', slug: blog-title'
            self._slug = re.sub('[^\w]+', '-', self._title.lower()).strip('-')
        re_entry = super(Entry, self).save(*args, **kwargs)

        # Store in search content
        self.update_search_index()
        return re_entry

    # Adds new entry to full text search table
    def update_search_index(self):
        exists = (FTSEntry
                    .select(FTSEntry.docid)
                    .where(FTSEntry.docid == self.id)
                    .exists()
                )
        content = '\n'.join((self._title, self._content))
        if exists:
            (FTSEntry
                .update({FTSEntry.content: content})
                .where(FTSEntry.docid == self.id)
                .execute()
            )
        else:
            FTSEntry.insert({
                FTSEntry.docid: self.id,
                FTSEntry.content: content
            }).execute()

    # Handles displaying published blog posts
    @classmethod
    def public(cls):
        return Entry.select().where(Entry._published == True)
    
    # Handles displaying drafted blog posts
    @classmethod
    def drafts(cls):
        return Entry.select().where(Entry._published == False)

    # Handles searching
    @classmethod
    def search(cls, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return empty query search
            return Entry.noop()
        else:
            search = ' '.join(words)
        return (Entry
                .select(Entry, FTSEntry.rank().alias('score'))
                .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
                .where(
                    FTSEntry.match(search) &
                    (Entry._published == True))
                .order_by(SQL('score')))


# Handles search database
class FTSEntry(FTSModel, db.Model):
    content = TextField()



