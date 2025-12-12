import os
from flask import Flask, render_template, request, redirect, session, send_file
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from io import BytesIO
from werkzeug.security import check_password_hash

from helpers import login_required
from schema import create_table, insert_project, insert_language, get_projects_names, get_project_details, get_project_languages, delete_project

app = Flask(__name__)
csrf = CSRFProtect(app)

load_dotenv()

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

create_table()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


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
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == os.getenv("ADMIN_USERNAME") and check_password_hash(os.getenv("ADMIN_PASSWORD"), password):
            session["logged_in"] = True
            return redirect("/admin")
        else:            
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
            return render_template("admin.html", error="Unsupported image format")
        
        img = img_file.read()
        if not img:
            return render_template("admin.html", error="Failed to read image file")
        
        if len(img) > 5 * 1024 * 1024: 
            return render_template("admin.html", error="Image file size exceeds 5MB limit")
        
        url = request.form.get("project-url")
        github = request.form.get("project-github")
        techs = request.form.get("project-tech")

        if not project_name or not desc or not url or not github or not techs:
            return render_template("admin.html", error="Please fill in all required fields")
        
        if not url.startswith("http://") and not url.startswith("https://"):
            return render_template("admin.html", error="Project URL must start with http:// or https://")
        
        if not github.startswith("http://") and not github.startswith("https://"):
            return render_template("admin.html", error="GitHub URL must start with http:// or https://")

        project_id = insert_project(project_name, desc, img, url, github)
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

