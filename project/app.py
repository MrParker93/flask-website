import yaml
from peewee import *
from flask import Flask

# Initialise Flask app
app = Flask(__name__)

# Load configurations
app.config.from_file('../config.yaml', load=yaml.safe_load)

# Read configurations to use
with open('config.yaml', 'r') as f:
    app_config = yaml.safe_load(f)

    # Initialise database
    db = MySQLDatabase(app_config['DATABASE']['DB'], autoconnect=True)

