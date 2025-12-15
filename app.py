import os
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, session, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from io import BytesIO
from PIL import Image
from werkzeug.security import check_password_hash

import config
from helpers import login_required
from schema import create_table, insert_project, insert_language, get_projects_names, get_project_details, get_project_languages, delete_project

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config.from_object(config.DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else config.ProductionConfig)

if not app.debug:
    handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10000, backupCount=3)
    handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(handler)
    
Session(app)

create_table()

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, message="Internal server error"), 500


# Public routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    projects = get_projects_names()
    return render_template('projects.html', projects=projects)



@app.route('/project/<int:project_id>')
def project(project_id):
    project = get_project_details(project_id)
    if not project:
        return render_template("project.html", error="Project not found")
    languages = get_project_languages(project_id)
    return render_template('project.html', project=project, languages=languages)


@app.route('/project_image/<int:project_id>')
def project_image(project_id):
    project = get_project_details(project_id)
    if project and project['image']:
        return send_file(BytesIO(project['image']), mimetype='image/png')
    return "Image not found", 404


# Admin routes
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == app.config["ADMIN_USERNAME"] and check_password_hash(app.config["ADMIN_PASSWORD"], password):
            session["logged_in"] = True
            return redirect("/admin")
        else:            
            app.logger.error(f"Failed login attempt for username: {username}")
            return render_template("login.html", error="Invalid username or password")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect('/')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not session.get('logged_in'):
        return redirect('/login')
    
    if request.method == 'POST':
        project_name = request.form.get("project-name")
        desc = request.form.get("desc")

        img_file = request.files.get("project-img")
        if not img_file or img_file.filename == '':
            return render_template("admin.html", error="Please provide an image")
        
        filename = img_file.filename
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if extension not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            app.logger.error(f"Unsupported image format attempted: {extension}")
            return render_template("admin.html", error="Unsupported image format")
        
        # Open and optimize image
        try:
            img = Image.open(img_file)
            img.thumbnail((800, 600))  # Resize keeping aspect ratio
            
            # Convert to RGB if needed (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save optimized image to bytes
            output = BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=85)
            img_data = output.getvalue()
            
            if len(img_data) > 5 * 1024 * 1024:
                app.logger.error("Image file size exceeds limit after processing")
                return render_template("admin.html", error="Image file size exceeds 5MB limit")
                
        except Exception as e:
            app.logger.error(f"Image processing error: {e}")
            return render_template("admin.html", error="Failed to process image")
                
        url = request.form.get("project-url")
        github = request.form.get("project-github")
        techs = request.form.get("project-tech")

        if not project_name or not desc or not url or not github or not techs:
            return render_template("admin.html", error="Please fill in all required fields")
        
        if not url.startswith("http://") and not url.startswith("https://"):
            return render_template("admin.html", error="Project URL must start with http:// or https://")
        
        if not github.startswith("http://") and not github.startswith("https://"):
            return render_template("admin.html", error="GitHub URL must start with http:// or https://")

        project_id = insert_project(project_name, desc, img_data, url, github)
        if not project_id:
            return render_template("admin.html", error="Failed to add project")

        for tech in techs.split(','):
            insert_language(project_id, tech.strip())

    return render_template('admin.html', projects=get_projects_names())


@app.route('/delete/<int:project_id>', methods=['POST'])
@login_required
def delete(project_id):
    delete_project(project_id)
    return redirect('/admin')
