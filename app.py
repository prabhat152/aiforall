from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail, Message
from functools import wraps
import re
import markdown2
from slugify import slugify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Ensure instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "contacts.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# User model for Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Contact Message Model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Blog Post Model
class BlogPost(db.Model):
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

# Create database tables
with app.app_context():
    try:
        db.create_all()
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

def send_notification_email(contact_message):
    try:
        msg = Message(
            subject=f'New Contact Form Submission from {contact_message.name}',
            recipients=['prabhat.kumar@aptinnova.com'],
            body=f'''
            New contact form submission received:
            
            Name: {contact_message.name}
            Email: {contact_message.email}
            Company: {contact_message.company}
            Message: {contact_message.message}
            
            Time: {contact_message.created_at}
            '''
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/blog')
def blog():
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('blog_post.html', post=post)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            company = request.form.get('company')
            message = request.form.get('message')

            # Create new contact message
            new_message = ContactMessage(
                name=name,
                email=email,
                company=company,
                message=message
            )

            # Save to database
            db.session.add(new_message)
            db.session.commit()

            # Send notification email
            send_notification_email(new_message)

            # Flash success message
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))

        except Exception as e:
            # Flash error message
            flash('Sorry, there was an error sending your message. Please try again.', 'error')
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_messages'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_messages'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/blog')
@login_required
def admin_blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/blog/new', methods=['GET', 'POST'])
@login_required
def admin_blog_new():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            content_format = request.form.get('content_format', 'markdown')
            thumbnail = request.form.get('thumbnail')
            embed_url = request.form.get('embed_url')
            embed_type = request.form.get('embed_type')
            is_published = request.form.get('is_published') == 'on'

            post = BlogPost(
                title=title,
                content=content,
                content_format=content_format,
                thumbnail=thumbnail,
                embed_url=embed_url,
                embed_type=embed_type,
                is_published=is_published
            )

            db.session.add(post)
            db.session.commit()

            flash('Blog post created successfully!', 'success')
            return redirect(url_for('admin_blog'))
        except Exception as e:
            flash(f'Error creating blog post: {str(e)}', 'error')
            return redirect(url_for('admin_blog_new'))

    return render_template('admin/blog_edit.html')

@app.route('/admin/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_blog_edit(id):
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.content_format = request.form.get('content_format', 'markdown')
            post.thumbnail = request.form.get('thumbnail')
            post.embed_url = request.form.get('embed_url')
            post.embed_type = request.form.get('embed_type')
            post.is_published = request.form.get('is_published') == 'on'
            post.slug = post._generate_slug(post.title)

            db.session.commit()
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('admin_blog'))
        except Exception as e:
            flash(f'Error updating blog post: {str(e)}', 'error')
            return redirect(url_for('admin_blog_edit', id=id))

    return render_template('admin/blog_edit.html', post=post)

@app.route('/admin/blog/<int:id>/delete', methods=['POST'])
@login_required
def admin_blog_delete(id):
    post = BlogPost.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting blog post: {str(e)}', 'error')
    return redirect(url_for('admin_blog'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 