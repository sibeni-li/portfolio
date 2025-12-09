import os
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from helpers import login_required
from schema import create_table, insert_project, insert_language, get_projects_names

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


load_dotenv()
create_table()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


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


# TODO
@app.route('/project/<int:project_id>')
def project(project_id):
    # Handle project details here
    pass


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


@login_required
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')


@login_required
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect('/login')
    
    if request.method == 'POST':
        # Handle admin actions here
        project_name = request.form.get("project-name")
        desc = request.form.get("desc")
        img = request.form.get("project-img")
        url = request.form.get("project-url")
        github = request.form.get("project-github")
        techs = request.form.get("project-tech")

        project_id = insert_project(project_name, desc, img, url, github)

        if project_id and techs:
            for tech in techs.split(','):
                insert_language(project_id, tech.strip())

    return render_template('admin.html')