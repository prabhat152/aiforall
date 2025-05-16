from datetime import datetime
import re
from flask_sqlalchemy import SQLAlchemy
import markdown2

db = SQLAlchemy()

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_format = db.Column(db.String(20), default='markdown')
    thumbnail = db.Column(db.String(500))  # URL to the thumbnail image
    embed_url = db.Column(db.String(500))
    embed_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = self._generate_slug(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)

    def _generate_slug(self, title):
        # Convert title to lowercase and replace spaces with hyphens
        slug = title.lower()
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove duplicate hyphens
        slug = re.sub(r'-+', '-', slug)
        return slug

    @property
    def formatted_content(self):
        if self.content_format == 'markdown':
            return markdown2.markdown(self.content, extras=['fenced-code-blocks', 'tables', 'header-ids'])
        return self.content 