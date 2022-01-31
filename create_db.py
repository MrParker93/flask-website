from project.app import db
from project.models import Post

# Create the databse and database tables
db.create_all()

# Commit the changes
db.session.commit()