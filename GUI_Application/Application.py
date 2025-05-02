from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import datetime

app = Flask(__name__)
app.secret_key = 'social_media_analysis_key'

# Database Configuration - read from config file
def get_db_config():
    try:
        with open('db_config.txt', 'r') as file:
            lines = file.readlines()
            config = {}
            for line in lines:
                key, value = line.strip().split('=')
                config[key] = value
            return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        # Default config if file cannot be read
        return {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'database': 'social_media_analysis'
        }

# Function to get database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**get_db_config())
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entry')
def entry():
    return render_template('entry.html')

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/results')
def results():
    return render_template('results.html')

# Data Entry Routes
@app.route('/data_entry')
def data_entry():
    return render_template('data_entry.html')

# Social Media Management
@app.route('/social_media', methods=['GET'])
def list_social_media():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM social_media")
        social_media = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('social_media.html', social_media=social_media)
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/social_media/add', methods=['GET', 'POST'])
def add_social_media():
    if request.method == 'POST':
        media_name = request.form['media_name']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO social_media (media_name) VALUES (%s)", (media_name,))
                conn.commit()
                flash(f"Social media '{media_name}' added successfully", "success")
            except Error as e:
                flash(f"Error adding social media: {e}", "danger")
            
            cursor.close()
            conn.close()
            return redirect(url_for('list_social_media'))
        
        flash("Database connection error", "danger")
    
    return render_template('add_social_media.html')

# Project Management
@app.route('/projects', methods=['GET'])
def list_projects():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.project_id, p.project_name, p.manager_first_name, p.manager_last_name, 
                i.institute_name, p.start_date, p.end_date 
            FROM projects p
            JOIN institutes i ON p.institute_id = i.institute_id
        """)
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('projects.html', projects=projects)
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        manager_first_name = request.form['manager_first_name']
        manager_last_name = request.form['manager_last_name']
        institute_name = request.form['institute_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if institute exists
            cursor.execute("SELECT institute_id FROM institutes WHERE institute_name = %s", (institute_name,))
            institute = cursor.fetchone()
            
            if not institute:
                # Create institute
                cursor.execute("INSERT INTO institutes (institute_name) VALUES (%s)", (institute_name,))
                institute_id = cursor.lastrowid
            else:
                institute_id = institute[0]
            
            # Create project
            cursor.execute("""
                INSERT INTO projects (project_name, manager_first_name, manager_last_name, 
                                     institute_id, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (project_name, manager_first_name, manager_last_name, 
                 institute_id, start_date, end_date))
            
            conn.commit()
            project_id = cursor.lastrowid
            
            # Handle project fields
            field_names = request.form.getlist('field_name')
            for field_name in field_names:
                if field_name.strip():
                    cursor.execute("""
                        INSERT INTO project_fields (project_id, field_name)
                        VALUES (%s, %s)
                    """, (project_id, field_name))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Project added successfully", "success")
            return redirect(url_for('list_projects'))
        
        flash("Database connection error", "danger")
    
    # GET request
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT institute_name FROM institutes")
        institutes = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('add_project.html', institutes=institutes)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/projects/<int:project_id>', methods=['GET'])
def view_project(project_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get project details
        cursor.execute("""
            SELECT p.project_id, p.project_name, p.manager_first_name, p.manager_last_name, 
                i.institute_name, p.start_date, p.end_date 
            FROM projects p
            JOIN institutes i ON p.institute_id = i.institute_id
            WHERE p.project_id = %s
        """, (project_id,))
        project = cursor.fetchone()
        
        if not project:
            flash("Project not found", "danger")
            return redirect(url_for('list_projects'))
        
        # Get project fields
        cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project_id,))
        fields = cursor.fetchall()
        
        # Get posts associated with this project
        cursor.execute("""
            SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time,
                   p.city, p.state, p.country, p.likes, p.dislikes, p.has_multimedia
            FROM posts p
            JOIN project_posts pp ON p.post_id = pp.post_id
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            WHERE pp.project_id = %s
        """, (project_id,))
        posts = cursor.fetchall()
        
        # Get analysis results for each post
        for post in posts:
            cursor.execute("""
                SELECT pf.field_name, ar.result_value
                FROM analysis_results ar
                JOIN project_fields pf ON ar.field_id = pf.field_id
                WHERE ar.project_id = %s AND ar.post_id = %s
            """, (project_id, post['post_id']))
            post['results'] = {result['field_name']: result['result_value'] for result in cursor.fetchall()}
        
        # Calculate field completion percentages
        field_stats = {}
        for field in fields:
            field_name = field['field_name']
            field_stats[field_name] = {'total': len(posts), 'filled': 0}
            
            for post in posts:
                if field_name in post['results'] and post['results'][field_name]:
                    field_stats[field_name]['filled'] += 1
        
        # Convert to percentages
        for field_name, stats in field_stats.items():
            if stats['total'] > 0:
                completion = (stats['filled'] / stats['total']) * 100
            else:
                completion = 0
            field_stats[field_name] = f"{completion:.1f}%"
        
        cursor.close()
        conn.close()
        
        return render_template('view_project.html', project=project, fields=fields, 
                               posts=posts, field_stats=field_stats)
    
    flash("Database connection error", "danger")
    return redirect(url_for('list_projects'))

# User Management
@app.route('/users', methods=['GET'])
def list_users():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.user_id, u.username, sm.media_name, u.first_name, u.last_name, 
                   u.country_of_residence, u.is_verified
            FROM users u
            JOIN social_media sm ON u.media_id = sm.media_id
        """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('users.html', users=users)
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        media_name = request.form['media_name']
        username = request.form['username']
        first_name = request.form['first_name'] or None
        last_name = request.form['last_name'] or None
        country_of_birth = request.form['country_of_birth'] or None
        country_of_residence = request.form['country_of_residence'] or None
        age = request.form['age'] or None
        gender = request.form['gender'] or None
        is_verified = 'is_verified' in request.form
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if social media exists
            cursor.execute("SELECT media_id FROM social_media WHERE media_name = %s", (media_name,))
            media = cursor.fetchone()
            
            if not media:
                # Create social media
                cursor.execute("INSERT INTO social_media (media_name) VALUES (%s)", (media_name,))
                media_id = cursor.lastrowid
            else:
                media_id = media[0]
            
            # Create user
            try:
                cursor.execute("""
                    INSERT INTO users (media_id, username, first_name, last_name, 
                                     country_of_birth, country_of_residence, age, 
                                     gender, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (media_id, username, first_name, last_name, 
                     country_of_birth, country_of_residence, age, 
                     gender, is_verified))
                
                conn.commit()
                flash("User added successfully", "success")
            except Error as e:
                flash(f"Error adding user: {e}", "danger")
            
            cursor.close()
            conn.close()
            return redirect(url_for('list_users'))
        
        flash("Database connection error", "danger")
    
    # GET request
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT media_name FROM social_media")
        social_media = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('add_user.html', social_media=social_media)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

# Post Management
@app.route('/posts', methods=['GET'])
def list_posts():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.post_id, LEFT(p.post_text, 100) AS post_preview, sm.media_name, 
                   u.username, p.post_time, p.likes, p.dislikes
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            ORDER BY p.post_time DESC
        """)
        posts = cursor.fetchall()
        
        # Add "..." to previews that are cut off
        for post in posts:
            if len(post['post_preview']) == 100:
                post['post_preview'] += "..."
        
        cursor.close()
        conn.close()
        return render_template('posts.html', posts=posts)
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/posts/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        media_name = request.form['media_name']
        username = request.form['username']
        post_text = request.form['post_text']
        post_time = request.form['post_time']
        city = request.form['city'] or None
        state = request.form['state'] or None
        country = request.form['country'] or None
        likes = request.form['likes'] or 0
        dislikes = request.form['dislikes'] or 0
        has_multimedia = 'has_multimedia' in request.form
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Get user ID
            cursor.execute("""
                SELECT u.user_id, sm.media_id FROM users u
                JOIN social_media sm ON u.media_id = sm.media_id
                WHERE sm.media_name = %s AND u.username = %s
            """, (media_name, username))
            user_info = cursor.fetchone()
            
            if not user_info:
                flash(f"User {username} on {media_name} not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('add_post'))
            
            user_id, media_id = user_info
            
            # Check if post already exists
            cursor.execute("""
                SELECT post_id FROM posts 
                WHERE user_id = %s AND media_id = %s AND post_time = %s
            """, (user_id, media_id, post_time))
            existing_post = cursor.fetchone()
            
            if existing_post:
                flash(f"Post already exists with ID {existing_post[0]}", "warning")
                post_id = existing_post[0]
            else:
                # Create post
                cursor.execute("""
                    INSERT INTO posts (user_id, media_id, post_text, post_time, city, state, 
                                     country, likes, dislikes, has_multimedia)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, media_id, post_text, post_time, city, state, 
                     country, likes, dislikes, has_multimedia))
                
                conn.commit()
                post_id = cursor.lastrowid
                flash("Post added successfully", "success")
            
            # Check if we need to associate with a project
            if 'project_id' in request.form and request.form['project_id']:
                project_id = request.form['project_id']
                
                # Check if association already exists
                cursor.execute("""
                    SELECT 1 FROM project_posts 
                    WHERE project_id = %s AND post_id = %s
                """, (project_id, post_id))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO project_posts (project_id, post_id)
                        VALUES (%s, %s)
                    """, (project_id, post_id))
                    conn.commit()
                    flash("Post associated with project", "success")
            
            cursor.close()
            conn.close()
            return redirect(url_for('list_posts'))
        
        flash("Database connection error", "danger")
    
    # GET request
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.username, sm.media_name
            FROM users u
            JOIN social_media sm ON u.media_id = sm.media_id
        """)
        users = cursor.fetchall()
        
        cursor.execute("SELECT project_id, project_name FROM projects")
        projects = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('add_post.html', users=users, projects=projects)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/posts/<int:post_id>', methods=['GET'])
def view_post(post_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get post details
        cursor.execute("""
            SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time,
                   p.city, p.state, p.country, p.likes, p.dislikes, p.has_multimedia
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            WHERE p.post_id = %s
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash("Post not found", "danger")
            return redirect(url_for('list_posts'))
        
        # Get reposts
        cursor.execute("""
            SELECT r.repost_id, u.username, sm.media_name, r.repost_time
            FROM reposts r
            JOIN users u ON r.user_id = u.user_id
            JOIN social_media sm ON u.media_id = sm.media_id
            WHERE r.post_id = %s
        """, (post_id,))
        reposts = cursor.fetchall()
        
        # Get projects associated with this post
        cursor.execute("""
            SELECT p.project_id, p.project_name
            FROM projects p
            JOIN project_posts pp ON p.project_id = pp.project_id
            WHERE pp.post_id = %s
        """, (post_id,))
        projects = cursor.fetchall()
        
        # Get analysis results for each project
        for project in projects:
            cursor.execute("""
                SELECT pf.field_name, ar.result_value
                FROM analysis_results ar
                JOIN project_fields pf ON ar.field_id = pf.field_id
                WHERE ar.project_id = %s AND ar.post_id = %s
            """, (project['project_id'], post_id))
            project['results'] = {result['field_name']: result['result_value'] for result in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        return render_template('view_post.html', post=post, reposts=reposts, projects=projects)
    
    flash("Database connection error", "danger")
    return redirect(url_for('list_posts'))

@app.route('/posts/repost', methods=['POST'])
def add_repost():
    post_id = request.form['post_id']
    media_name = request.form['media_name']
    username = request.form['username']
    repost_time = request.form['repost_time']
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("""
            SELECT user_id FROM users u
            JOIN social_media sm ON u.media_id = sm.media_id
            WHERE sm.media_name = %s AND u.username = %s
        """, (media_name, username))
        user_result = cursor.fetchone()
        
        if not user_result:
            flash(f"User {username} on {media_name} not found", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('view_post', post_id=post_id))
        
        user_id = user_result[0]
        
        # Add repost
        cursor.execute("""
            INSERT INTO reposts (post_id, user_id, repost_time)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, repost_time))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Repost added successfully", "success")
        return redirect(url_for('view_post', post_id=post_id))
    
    flash("Database connection error", "danger")
    return redirect(url_for('view_post', post_id=post_id))

# Analysis Results
@app.route('/analysis/add', methods=['GET', 'POST'])
def add_analysis():
    if request.method == 'POST':
        project_id = request.form['project_id']
        post_id = request.form['post_id']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Get all fields for the project
            cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project_id,))
            project_fields = cursor.fetchall()
            
            # Check if post is associated with project
            cursor.execute("SELECT 1 FROM project_posts WHERE project_id = %s AND post_id = %s", (project_id, post_id))
            if not cursor.fetchone():
                # Associate post with project
                cursor.execute("INSERT INTO project_posts (project_id, post_id) VALUES (%s, %s)", (project_id, post_id))
                conn.commit()
            
            # Process field values
            for field_id, field_name in project_fields:
                field_key = f"field_{field_id}"
                if field_key in request.form:
                    result_value = request.form[field_key]
                    
                    # Check if result already exists
                    cursor.execute("""
                        SELECT result_id FROM analysis_results 
                        WHERE project_id = %s AND post_id = %s AND field_id = %s
                    """, (project_id, post_id, field_id))
                    existing_result = cursor.fetchone()
                    
                    if existing_result:
                        # Update existing result
                        cursor.execute("""
                            UPDATE analysis_results SET result_value = %s
                            WHERE project_id = %s AND post_id = %s AND field_id = %s
                        """, (result_value, project_id, post_id, field_id))
                    else:
                        # Create new result
                        cursor.execute("""
                            INSERT INTO analysis_results (project_id, post_id, field_id, result_value)
                            VALUES (%s, %s, %s, %s)
                        """, (project_id, post_id, field_id, result_value))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Analysis results saved successfully", "success")
            return redirect(url_for('view_project', project_id=project_id))
        
        flash("Database connection error", "danger")
    
    # GET request
    project_id = request.args.get('project_id')
    post_id = request.args.get('post_id')
    
    if not project_id or not post_id:
        flash("Missing project or post information", "danger")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get project details
        cursor.execute("SELECT project_id, project_name FROM projects WHERE project_id = %s", (project_id,))
        project = cursor.fetchone()
        
        if not project:
            flash("Project not found", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        
        # Get post details
        cursor.execute("""
            SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            WHERE p.post_id = %s
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash("Post not found", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('view_project', project_id=project_id))
        
        # Get fields for this project
        cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project_id,))
        fields = cursor.fetchall()
        
        # Get existing results
        cursor.execute("""
            SELECT field_id, result_value
            FROM analysis_results
            WHERE project_id = %s AND post_id = %s
        """, (project_id, post_id))
        existing_results = {result['field_id']: result['result_value'] for result in cursor.fetchall()}

        cursor.close()
        conn.close()
        
        return render_template('add_analysis.html', project=project, post=post, 
                               fields=fields, existing_results=existing_results)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

# Query Routes
@app.route('/query/posts', methods=['GET', 'POST'])
def query_posts():
    if request.method == 'POST':
        media_name = request.form.get('media_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Build the query
        query = """
            SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            WHERE 1=1
        """
        params = []
        
        if media_name:
            query += " AND sm.media_name = %s"
            params.append(media_name)
        
        if start_date:
            query += " AND p.post_time >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND p.post_time <= %s"
            params.append(end_date)
        
        if username and media_name:
            query += " AND u.username = %s"
            params.append(username)
        
        if first_name:
            query += " AND u.first_name = %s"
            params.append(first_name)
        
        if last_name:
            query += " AND u.last_name = %s"
            params.append(last_name)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            posts = cursor.fetchall()
            
            # Get projects for each post
            for post in posts:
                cursor.execute("""
                    SELECT p.project_name
                    FROM projects p
                    JOIN project_posts pp ON p.project_id = pp.project_id
                    WHERE pp.post_id = %s
                """, (post['post_id'],))
                projects = cursor.fetchall()
                post['projects'] = [project['project_name'] for project in projects]
            
            cursor.close()
            conn.close()
            
            return render_template('query_posts_results.html', posts=posts, 
                                  media_name=media_name, start_date=start_date, 
                                  end_date=end_date, username=username, 
                                  first_name=first_name, last_name=last_name)
        
        flash("Database connection error", "danger")
    
    # GET request or failed query
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT media_name FROM social_media")
        social_media = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('query_posts.html', social_media=social_media)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

from flask import jsonify

@app.route('/search-posts', methods=['GET'])
def search_posts():
    media_name = request.args.get('socialMedia')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    username = request.args.get('username')
    first_name = request.args.get('firstName')
    last_name = request.args.get('lastName')

    query = """
        SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        JOIN social_media sm ON p.media_id = sm.media_id
        WHERE 1=1
    """
    params = []

    if media_name:
        query += " AND sm.media_name = %s"
        params.append(media_name)

    if start_date:
        query += " AND p.post_time >= %s"
        params.append(start_date)

    if end_date:
        query += " AND p.post_time <= %s"
        params.append(end_date)

    if username:
        query += " AND u.username = %s"
        params.append(username)

    if first_name:
        query += " AND u.first_name = %s"
        params.append(first_name)

    if last_name:
        query += " AND u.last_name = %s"
        params.append(last_name)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        posts = cursor.fetchall()

        # Get projects for each post
        for post in posts:
            cursor.execute("""
                SELECT p.project_name
                FROM projects p
                JOIN project_posts pp ON p.project_id = pp.project_id
                WHERE pp.post_id = %s
            """, (post['post_id'],))
            projects = cursor.fetchall()
            post['projects'] = [project['project_name'] for project in projects]

        cursor.close()
        conn.close()

        return jsonify(posts)

    return jsonify({'error': 'Database connection error'}), 500



@app.route('/query/project', methods=['GET', 'POST'])
def query_project():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get project details
            cursor.execute("""
                SELECT p.project_id, p.project_name, p.manager_first_name, p.manager_last_name, 
                    i.institute_name, p.start_date, p.end_date 
                FROM projects p
                JOIN institutes i ON p.institute_id = i.institute_id
                WHERE p.project_name = %s
            """, (project_name,))
            project = cursor.fetchone()
            
            if not project:
                flash("Project not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('query_project'))
            
            # Get fields for this project
            cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project['project_id'],))
            fields = cursor.fetchall()
            
            # Get posts associated with this project
            cursor.execute("""
                SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
                FROM posts p
                JOIN project_posts pp ON p.post_id = pp.post_id
                JOIN users u ON p.user_id = u.user_id
                JOIN social_media sm ON p.media_id = sm.media_id
                WHERE pp.project_id = %s
            """, (project['project_id'],))
            posts = cursor.fetchall()
            
            # Get analysis results for each post
            for post in posts:
                cursor.execute("""
                    SELECT pf.field_name, ar.result_value
                    FROM analysis_results ar
                    JOIN project_fields pf ON ar.field_id = pf.field_id
                    WHERE ar.project_id = %s AND ar.post_id = %s
                """, (project['project_id'], post['post_id']))
                post['results'] = {result['field_name']: result['result_value'] for result in cursor.fetchall()}
            
            # Calculate field completion percentages
            field_stats = {}
            for field in fields:
                field_name = field['field_name']
                field_stats[field_name] = {'total': len(posts), 'filled': 0}
                
                for post in posts:
                    if field_name in post['results'] and post['results'][field_name]:
                        field_stats[field_name]['filled'] += 1
            
            # Convert to percentages
            for field_name, stats in field_stats.items():
                if stats['total'] > 0:
                    completion = (stats['filled'] / stats['total']) * 100
                else:
                    completion = 0
                field_stats[field_name] = f"{completion:.1f}%"
            
            cursor.close()
            conn.close()
            
            return render_template('query_project_results.html', project=project, 
                                  fields=fields, posts=posts, field_stats=field_stats)
        
        flash("Database connection error", "danger")
    
    # GET request or failed query
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT project_name FROM projects")
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('query_project.html', projects=projects)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

@app.route('/query/posts_experiments', methods=['GET', 'POST'])
def query_posts_experiments():
    if request.method == 'POST':
        media_name = request.form.get('media_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Build the query
        query = """
            SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            JOIN social_media sm ON p.media_id = sm.media_id
            WHERE 1=1
        """
        params = []
        
        if media_name:
            query += " AND sm.media_name = %s"
            params.append(media_name)
        
        if start_date:
            query += " AND p.post_time >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND p.post_time <= %s"
            params.append(end_date)
        
        if username and media_name:
            query += " AND u.username = %s"
            params.append(username)
        
        if first_name:
            query += " AND u.first_name = %s"
            params.append(first_name)
        
        if last_name:
            query += " AND u.last_name = %s"
            params.append(last_name)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            posts = cursor.fetchall()
            
            if not posts:
                flash("No posts found matching the criteria", "warning")
                cursor.close()
                conn.close()
                return redirect(url_for('query_posts_experiments'))
            
            post_ids = [post['post_id'] for post in posts]
            
            # Get all projects associated with these posts
            placeholders = ', '.join(['%s'] * len(post_ids))
            query = f"""
                SELECT DISTINCT p.project_id, p.project_name
                FROM projects p
                JOIN project_posts pp ON p.project_id = pp.project_id
                WHERE pp.post_id IN ({placeholders})
            """
            cursor.execute(query, post_ids)
            projects = cursor.fetchall()
            
            # Get detailed project information
            project_details = []
            for project in projects:
                # Get project info
                cursor.execute("""
                    SELECT p.project_id, p.project_name, p.manager_first_name, p.manager_last_name, 
                           i.institute_name, p.start_date, p.end_date
                    FROM projects p
                    JOIN institutes i ON p.institute_id = i.institute_id
                    WHERE p.project_id = %s
                """, (project['project_id'],))
                project_info = cursor.fetchone()
                
                # Get fields for this project
                cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", 
                             (project['project_id'],))
                fields = cursor.fetchall()
                
                # Get posts for this project (from the filtered list)
                cursor.execute(f"""
                    SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
                    FROM posts p
                    JOIN project_posts pp ON p.post_id = pp.post_id
                    JOIN users u ON p.user_id = u.user_id
                    JOIN social_media sm ON p.media_id = sm.media_id
                    WHERE pp.project_id = %s AND p.post_id IN ({placeholders})
                """, [project['project_id']] + post_ids)
                project_posts = cursor.fetchall()
                
                # Get analysis results for each post
                for post in project_posts:
                    cursor.execute("""
                        SELECT pf.field_name, ar.result_value
                        FROM analysis_results ar
                        JOIN project_fields pf ON ar.field_id = pf.field_id
                        WHERE ar.project_id = %s AND ar.post_id = %s
                    """, (project['project_id'], post['post_id']))
                    post['results'] = {result['field_name']: result['result_value'] 
                                       for result in cursor.fetchall()}
                
                # Calculate field completion percentages
                field_stats = {}
                for field in fields:
                    field_name = field['field_name']
                    field_stats[field_name] = {'total': len(project_posts), 'filled': 0}
                    
                    for post in project_posts:
                        if field_name in post['results'] and post['results'][field_name]:
                            field_stats[field_name]['filled'] += 1
                
                # Convert to percentages
                for field_name, stats in field_stats.items():
                    if stats['total'] > 0:
                        completion = (stats['filled'] / stats['total']) * 100
                    else:
                        completion = 0
                    field_stats[field_name] = f"{completion:.1f}%"
                
                project_details.append({
                    'info': project_info,
                    'fields': fields,
                    'posts': project_posts,
                    'field_stats': field_stats
                })
            
            cursor.close()
            conn.close()
            
            return render_template('query_posts_experiments_results.html', 
                                  posts=posts, project_details=project_details,
                                  media_name=media_name, start_date=start_date, 
                                  end_date=end_date, username=username, 
                                  first_name=first_name, last_name=last_name)
        
        flash("Database connection error", "danger")
    
    # GET request or failed query
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT media_name FROM social_media")
        social_media = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('query_posts_experiments.html', social_media=social_media)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/experiment_query', methods=['GET', 'POST'])
def experiment_query():
    if request.method == 'POST':
        experiment_name = request.form.get('experiment_name')
        
        if not experiment_name:
            flash('Please enter an experiment name', 'danger')
            return redirect(url_for('experiment_query'))
        
        result = query_experiment(experiment_name)
        
        if result['status'] == 'error':
            flash(result['message'], 'danger')
            return redirect(url_for('experiment_query'))
        
        return render_template(
            'experiment_results.html',
            project=result['project'],
            fields=result['fields'],
            posts=result['posts'],
            field_stats=result['field_stats']
        )
    
    # GET request - show form to query experiment
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT project_name FROM projects")
        experiments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('experiment_query.html', experiments=experiments)
    
    flash('Database connection failed', 'danger')
    return redirect(url_for('index'))

def query_experiment(experiment_name):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get project details
            cursor.execute("""
                SELECT project_id, project_name, manager_first_name, manager_last_name, 
                       institute_id, start_date, end_date
                FROM projects 
                WHERE project_name = %s
            """, (experiment_name,))
            
            project = cursor.fetchone()
            
            if not project:
                return {"status": "error", "message": "Experiment not found"}
            
            # Get fields for this project
            cursor.execute("""
                SELECT field_id, field_name
                FROM project_fields
                WHERE project_id = %s
            """, (project['project_id'],))
            
            fields = cursor.fetchall()
            
            # Get posts associated with this project
            cursor.execute("""
                SELECT pp.post_id, p.post_text, sm.media_name, u.username, p.post_time
                FROM project_posts pp
                JOIN posts p ON pp.post_id = p.post_id
                JOIN users u ON p.user_id = u.user_id
                JOIN social_media sm ON p.media_id = sm.media_id
                WHERE pp.project_id = %s
            """, (project['project_id'],))
            
            posts = cursor.fetchall()
            
            # Get analysis results for each post
            for post in posts:
                cursor.execute("""
                    SELECT pf.field_name, ar.result_value
                    FROM analysis_results ar
                    JOIN project_fields pf ON ar.field_id = pf.field_id
                    WHERE ar.project_id = %s AND ar.post_id = %s
                """, (project['project_id'], post['post_id']))
                
                results = cursor.fetchall()
                post['results'] = {result['field_name']: result['result_value'] for result in results}
            
            # Calculate field statistics
            field_stats = {}
            for field in fields:
                field_name = field['field_name']
                field_stats[field_name] = {'total': len(posts), 'filled': 0}
                
                for post in posts:
                    if field_name in post['results'] and post['results'][field_name]:
                        field_stats[field_name]['filled'] += 1
            
            # Convert to percentages
            for field_name, stats in field_stats.items():
                if stats['total'] > 0:
                    completion = (stats['filled'] / stats['total']) * 100
                else:
                    completion = 0
                field_stats[field_name]['percentage'] = f"{completion:.1f}%"
            
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "project": project,
                "fields": fields,
                "posts": posts,
                "field_stats": field_stats
            }
            
        except Error as e:
            print(f"Error querying experiment: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn.is_connected():
                conn.close()
    
    return {"status": "error", "message": "Database connection failed"}