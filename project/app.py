import yaml
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialise Flask app
app = Flask(__name__)

# Load configurations
app.config.from_file('..config/dev.yaml', load=yaml.safe_load)

# Initialize the database
db = SQLAlchemy(app=app)

# Read configurations to use
with open('config/dev.yaml', 'r') as f:
    app_config = yaml.safe_load(f)

