from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
    # Import models here to ensure they are registered with SQLAlchemy
    from .blog import BlogPost
    
    # Create all tables
    with app.app_context():
        db.create_all() 