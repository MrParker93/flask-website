import sqlite3
from flask import Flask, g

# Create database path
DATABASE = 'flaskr.db'

# Create and initialize a new Flask app
app = Flask(__name__)

# Load the app configuration
app.config.from_object(__name__)

# Connect to database
def connect_db():
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
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
