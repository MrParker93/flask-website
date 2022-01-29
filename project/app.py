from flask import Flask

# Create database path
DATABASE = 'flaskr.db'

# Create and initialize a new Flask app
app = Flask(__name__)

# Load the app configuration
app.config.from_object(__name__)

@app.route('/')
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()