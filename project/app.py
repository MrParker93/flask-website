from flask import Flask

# Create and initialize a new Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()