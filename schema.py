import sqlite3

# Create the database and tables if they don't exist
def create_table():
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                image BLOB,  
                site_url TEXT,   
                github_url TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS languages (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                project_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB error during table creation: {e}")
    finally:
        if conn:
            conn.close()

# Insert functions

def insert_project(name, description, image, site_url, github_url):
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO projects (name, description, image, site_url, github_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, image, site_url, github_url))
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        print(f"DB error during project insertion: {e}")
        return None
    finally:
        if conn:
            conn.close()

def insert_language(project_id, language):
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO languages (project_id, language)
            VALUES (?, ?)
        ''', (project_id, language))
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB error during language insertion: {e}")
    finally:
        if conn:
            conn.close()

# Fetch functions

def get_projects_names():
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, name FROM projects')
        projects = c.fetchall()
        return projects
    except sqlite3.Error as e:
        print(f"DB error during fetching project names: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_project_details(project_id):
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = c.fetchone()
        return project
    except sqlite3.Error as e:
        print(f"DB error during fetching project details: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_project_languages(project_id):
    conn = None
    try:
        conn = sqlite3.connect('projects.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT language FROM languages WHERE project_id = ?', (project_id,))
        languages = c.fetchall()
        return languages
    except sqlite3.Error as e:
        print(f"DB error during fetching project languages: {e}")
        return []
    finally:
        if conn:
            conn.close()