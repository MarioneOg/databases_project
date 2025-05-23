from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import datetime

app = Flask(__name__)
app.secret_key = 'social_media_analysis_key'


# Function to get database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="myuser",
            password="mypassword",
            database="social_media_analysis"
        )

        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
@app.route('/connect-db', methods=['GET', 'POST'])
def connect_db():
    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="myuser",
                password="mypassword"
            )

            if conn:
                # cursor = conn.cursor()
                # cursor.execute("SELECT 1")
                # cursor.fetchall() 
                # cursor.close()
                # conn.close()
                cursor = conn.cursor()

                with open("GUI_Application/Schema.sql", "r") as f:
                    sql = f.read()

                for result in cursor.execute(sql, multi=True):
                    pass

                conn.commit()
                cursor.close()

                flash("Database connection successful", "success")
            else:
                flash("Database connection failed", "danger")
        except Exception as e:
            flash(f"Error connecting to database: {e}", "danger")
    
        return redirect(url_for('index'))

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

@app.route('/experiment_query')
def expirement_query():
    return render_template('experiment_query.html')

@app.route('/experiment_result')
def experiment_result():
    return render_template('experiment_result.html')

@app.route('/post-results', methods=['GET'])
def post_results(posts):
    query = request.args.to_dict()
    return render_template('post_results.html', query=query, posts=posts)

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

def check_institute(conn, institute_name):
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Institute WHERE name = %s", (institute_name,))
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO Institute (name) VALUES (%s)", (institute_name,))
        conn.commit()
    cursor.close()

@app.route('/projects/add', methods=['GET', 'POST'])
def add_project_form():
    if request.method == 'POST':
        project_name = request.form.get('project_name').strip()
        manager_first_name = request.form.get('manager_first_name') or None
        manager_last_name = request.form.get('manager_last_name') or None
        institute_name = request.form.get('institute_name') or None
        start_date = request.form.get('start_date') or None
        end_date = request.form.get('end_date') or None

        if start_date and end_date and start_date > end_date:
            flash("Start date cannot be after end date", "danger")
            return redirect(url_for('entry'))
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if institute exists
            if institute_name:
                check_institute(conn, institute_name)
            # else:
            #     institute_id = institute[0]
            
            # Create project
            cursor.execute("""
                SELECT * FROM Project
                WHERE name = %s
            """, (project_name,))
            check_project = cursor.fetchone()

            if not check_project:
                cursor.execute("""
                    INSERT INTO Project (name, manager_firstname, manager_lastname, 
                                     institute_name, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (project_name, manager_first_name, manager_last_name, 
                institute_name, start_date, end_date))
                conn.commit()
            else:
                # Update only provided fields
                update_fields = []
                update_values = []

                if manager_first_name:
                    update_fields.append("manager_firstname = %s")
                    update_values.append(manager_first_name)

                if manager_last_name:
                    update_fields.append("manager_lastname = %s")
                    update_values.append(manager_last_name)

                if institute_name:
                    check_institute(conn, institute_name)
                    update_fields.append("institute_name = %s")
                    update_values.append(institute_name)

                if start_date:
                    update_fields.append("start_date = %s")
                    update_values.append(start_date)

                if end_date:
                    update_fields.append("end_date = %s")
                    update_values.append(end_date)

                if update_fields:
                    update_query = f"""
                        UPDATE Project 
                        SET {', '.join(update_fields)}
                        WHERE name = %s
                    """
                    update_values.append(project_name)
                    cursor.execute(update_query, tuple(update_values))
                    conn.commit()
                else:
                    flash("Post already exists", "danger")
                    cursor.close()
                    conn.close()
                    return redirect(url_for('entry'))
            
            cursor.close()
            conn.close()
            
            flash("Project added successfully", "success")
            return redirect(url_for('entry'))
        
        flash("Database connection error", "danger")

        
def add_field(conn, field_name, project_name):
    cursor = conn.cursor()

    # Check if the field exists
    cursor.execute("""
        SELECT * FROM Field
        WHERE field_name = %s AND project_name = %s
    """, (field_name, project_name))
    check_field = cursor.fetchone()

    if not check_field:
        # Insert new field
        cursor.execute("""
            INSERT INTO Field (field_name, project_name)
            VALUES (%s, %s)
        """, (field_name, project_name))
        conn.commit()

    cursor.close()

def add_analysis(conn, project_name, username, social_media, post_time, field_name, analysis):
    cursor = conn.cursor()

    # Check if analysis exists
    cursor.execute("""
        SELECT * FROM Analysis_Result
        WHERE project_name = %s AND post_username = %s AND post_social_media = %s AND post_time = %s AND field_name = %s
    """, (project_name, username, social_media, post_time, field_name))
    check_analysis = cursor.fetchone()

    if not check_analysis:
        # Insert new analysis
        cursor.execute("""
            INSERT INTO Analysis_Result (project_name, post_username, post_social_media, post_time, field_name, analysis)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (project_name, username, social_media, post_time, field_name, analysis))
        conn.commit()
    elif analysis:
        # Update existing analysis
        cursor.execute("""
            UPDATE Analysis_Result
            SET analysis = %s
            WHERE project_name = %s AND post_username = %s AND post_social_media = %s AND post_time = %s AND field_name = %s
        """, (analysis, project_name, username, social_media, post_time, field_name))
        conn.commit()
    else:
        flash("Analysis already exists", "danger")
        cursor.close()
        return redirect(url_for('entry'))

    cursor.close()

def find_project(conn, project_name):
    cursor = conn.cursor()

    # Find user
    cursor.execute("""
        SELECT * FROM Project
        WHERE name = %s
    """, (project_name,))
    project = cursor.fetchone()

    if project:
        return True
    else:
        return False

def find_user(conn, username, social_media):
    cursor = conn.cursor()

    # Find user
    cursor.execute("""
        SELECT * FROM User
        WHERE username = %s AND social_media = %s
    """, (username, social_media))
    user = cursor.fetchone()

    if user:
        return True
    else:
        return False
    
def find_post(conn, username, social_media, post_time):
    cursor = conn.cursor()

    # Find user
    cursor.execute("""
        SELECT * FROM Post
        WHERE post_username = %s AND post_social_media = %s AND post_time = %s
    """, (username, social_media, post_time))
    post = cursor.fetchone()

    if post:
        return True
    else:
        return False

        
@app.route('/analysis/add', methods=['GET', 'POST'])
def add_analysis_form():
    if request.method == 'POST':
        # Debug: Print all form data received
        print("Form data received:", request.form)
        
        try:
            # Get form data
            project_name = request.form.get('project_name', '').strip()
            username = request.form.get('username', '').strip()
            social_media = request.form.get('social_media', '').strip().lower()
            post_time_raw = request.form.get('post_time', '')
            field_name = request.form.get('field_name', '').strip().lower()
            analysis = request.form.get('analysis', None)
            
            # Validate required fields
            if not project_name:
                flash("Project name is required", "danger")
                return redirect(url_for('entry'))
                
            if not username:
                flash("Username is required", "danger")
                return redirect(url_for('entry'))
                
            if not social_media:
                flash("Social media is required", "danger")
                return redirect(url_for('entry'))
                
            if not post_time_raw:
                flash("Post time is required", "danger")
                return redirect(url_for('entry'))
                
            if not field_name:
                flash("Field name is required", "danger")
                return redirect(url_for('entry'))
            
            # Format post time properly
            post_time = post_time_raw.replace('T', ' ')
            if len(post_time) <= 16:  # If time doesn't include seconds
                post_time += ":00"
                
            print(f"Processing analysis form with data:")
            print(f"Project: '{project_name}'")
            print(f"Username: '{username}'")
            print(f"Social Media: '{social_media}'")
            print(f"Post Time: '{post_time}'")
            print(f"Field: '{field_name}'")
            print(f"Analysis: '{analysis}'")
            
            conn = get_db_connection()
            if not conn:
                flash("Database connection error", "danger")
                return redirect(url_for('entry'))
                
            cursor = conn.cursor()
            
            # Check if project exists
            cursor.execute("SELECT name FROM Project WHERE name = %s", (project_name,))
            project = cursor.fetchone()
            
            if not project:
                flash(f"Project '{project_name}' not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('entry'))
                
            # Check if user exists
            cursor.execute("SELECT username FROM User WHERE username = %s AND social_media = %s", 
                        (username, social_media))
            user = cursor.fetchone()
            
            if not user:
                flash(f"User '{username}' on '{social_media}' not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('entry'))
                
            # Check if post exists
            cursor.execute("""
                SELECT post_username FROM Post 
                WHERE post_username = %s AND post_social_media = %s AND post_time = %s
            """, (username, social_media, post_time))
            post = cursor.fetchone()
            
            if not post:
                flash(f"Post by '{username}' on '{social_media}' at '{post_time}' not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('entry'))

            # Add field to project
            try:
                cursor.execute("""
                    INSERT IGNORE INTO Field (field_name, project_name) 
                    VALUES (%s, %s)
                """, (field_name, project_name))
                conn.commit()
            except Exception as e:
                print(f"Error adding field: {str(e)}")
                flash(f"Error adding field: {str(e)}", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('entry'))
                
            # Check if analysis already exists
            cursor.execute("""
                SELECT * FROM Analysis_Result 
                WHERE project_name = %s 
                  AND post_username = %s 
                  AND post_social_media = %s 
                  AND post_time = %s 
                  AND field_name = %s
            """, (project_name, username, social_media, post_time, field_name))
            existing_analysis = cursor.fetchone()
            
            try:
                if existing_analysis:
                    # Update existing analysis
                    cursor.execute("""
                        UPDATE Analysis_Result
                        SET analysis = %s
                        WHERE project_name = %s 
                          AND post_username = %s 
                          AND post_social_media = %s 
                          AND post_time = %s 
                          AND field_name = %s
                    """, (analysis, project_name, username, social_media, post_time, field_name))
                    flash("Analysis updated successfully", "success")
                else:
                    # Insert new analysis
                    cursor.execute("""
                        INSERT INTO Analysis_Result 
                        (project_name, post_username, post_social_media, post_time, field_name, analysis)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (project_name, username, social_media, post_time, field_name, analysis))
                    flash("Analysis added successfully", "success")
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error saving analysis: {str(e)}")
                flash(f"Error saving analysis: {str(e)}", "danger")
            finally:
                cursor.close()
                conn.close()
                
            return redirect(url_for('entry'))
                
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('entry'))
            
    # GET request - redirect to entry form
    return redirect(url_for('entry'))

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

def add_social_media(conn, social_media):
    cursor = conn.cursor()

    # Check if the social media platform already exists
    cursor.execute("SELECT name FROM Social_Media WHERE name = %s", (social_media,))
    result = cursor.fetchone()

    if not result:
        # Insert it if it's not already in the table
        cursor.execute("INSERT INTO Social_Media (name) VALUES (%s)", (social_media,))
        conn.commit()

    cursor.close()

# Helper functions for Add Post Data Entry
def add_user(conn, username, social_media, first_name, last_name, country_birth, country_residence, age, gender, verified):
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("""
        SELECT * FROM User
        WHERE username = %s AND social_media = %s
    """, (username, social_media))
    user = cursor.fetchone()

    if not user:
        # Insert new user
        cursor.execute("""
            INSERT INTO User (username, social_media, first_name, last_name,
                               country_of_birth, country_of_residence, age, gender, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, social_media, first_name, last_name, country_birth,
              country_residence, age, gender, verified))
        conn.commit()
        cursor.close()
        return "User added successfully", "success"
    else:
        update_fields = []
        update_values = []

        if first_name:
            update_fields.append("first_name = %s")
            update_values.append(first_name)
        if last_name:
            update_fields.append("last_name = %s")
            update_values.append(last_name)
        if country_birth:
            update_fields.append("country_of_birth = %s")
            update_values.append(country_birth)
        if country_residence:
            update_fields.append("country_of_residence = %s")
            update_values.append(country_residence)
        if age:
            update_fields.append("age = %s")
            update_values.append(age)
        if verified is not None:
            update_fields.append("is_verified = %s")
            update_values.append(verified)

        if update_fields:
            update_query = f"""
                UPDATE User
                SET {', '.join(update_fields)}
                WHERE username = %s AND social_media = %s
            """
            update_values.extend([username, social_media])
            cursor.execute(update_query, tuple(update_values))
            conn.commit()
            cursor.close()
            return "User updated successfully", "success"
        else:
            cursor.close()
            return "User already exists", "danger"

@app.route('/user/add', methods=['GET', 'POST'])
def add_user_form():
    if request.method == 'POST':
        username = request.form['username'].strip()
        social_media = request.form['social_media'].lower().strip()
        first_name = request.form['first_name'] or None
        last_name = request.form['last_name'] or None
        country_birth = request.form['country_birth'].lower() or None
        country_residence = request.form['country_residence'].lower() or None
        age = request.form['age'] or None
        if age:
            try:
                ageInt = int(age)
                if ageInt < 0:
                    flash("Age must be a positive integer, try again", "danger")
                    return redirect(url_for('entry'))
            except ValueError:
                flash("Age must be a positive integer, try again", "danger")
                return redirect(url_for('entry'))

        gender = request.form['gender'].lower() or None
        verified = request.form['verified'] or None
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            add_social_media(conn, social_media)
            message, status = add_user(conn, username, social_media, first_name, last_name, 
                     country_birth, country_residence, age, gender, verified)
            
            cursor.close()
            conn.close()
            
            flash(message, status)
            return redirect(url_for('entry'))
        
        flash("Database connection error", "danger")
        return redirect(url_for('entry'))

def add_post(conn, username, social_media, post_time, text, likes, dislikes, city, state, country, multimedia):
    cursor = conn.cursor()

    # Add the social media to the social media database
    cursor.execute("""
        SELECT * FROM Social_Media
        WHERE name = %s
    """, (social_media,))
    check_media = cursor.fetchone()

    if not check_media:
        cursor.execute("""
            INSERT INTO Social_Media (name)
            VALUES (%s)
        """, (social_media,))
        conn.commit()

    # Check if original post exists
    cursor.execute("""
        SELECT * FROM Post
        WHERE post_username = %s AND post_social_media = %s AND post_time = %s
    """, (username, social_media, post_time))
    check_post = cursor.fetchone()

    if not check_post:
        cursor.execute("""
            INSERT INTO Post (post_username, post_social_media, post_time, text, likes, dislikes, location_city, location_state, location_country, has_multimedia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, social_media, post_time, text, likes, dislikes, city, state, country, multimedia))
        conn.commit()
    else:
        update_fields = []
        update_values = []

        if text is not None:
            update_fields.append("text = %s")
            update_values.append(text)
        if likes is not None:
            update_fields.append("likes = %s")
            update_values.append(likes)
        if dislikes is not None:
            update_fields.append("dislikes = %s")
            update_values.append(dislikes)
        if city is not None:
            update_fields.append("location_city = %s")
            update_values.append(city)
        if state is not None:
            update_fields.append("location_state = %s")
            update_values.append(state)
        if country is not None:
            update_fields.append("location_country = %s")
            update_values.append(country)
        if multimedia is not None:
            update_fields.append("has_multimedia = %s")
            update_values.append(multimedia)
        
        if update_fields:
            update_query = f"""
                UPDATE Post
                SET {', '.join(update_fields)}
                WHERE post_username = %s AND post_social_media = %s AND post_time = %s
            """
            update_values.extend([username, social_media, post_time])
            cursor.execute(update_query, tuple(update_values))
            conn.commit()
        else:
            flash("Post already exists", "danger")
            cursor.close()
            return redirect(url_for('entry'))

    cursor.close()

def add_repost(conn,
               repost_username, repost_social_media, repost_time,
               repost_city, repost_state, repost_country,
               repost_likes, repost_dislikes, repost_multimedia,
               original_username, original_social_media, original_post_time):
    cursor = conn.cursor()


    # Check if repost social media exists
    cursor.execute("SELECT name FROM Social_Media WHERE name = %s", (repost_social_media,))
    check_media = cursor.fetchone()

    if not check_media:
        cursor.execute("INSERT INTO Social_Media (name) VALUES (%s)", (repost_social_media,))
        conn.commit()

    print("Checking user")
    # Check if repost user exists
    cursor.execute("""
        SELECT * FROM User
        WHERE username = %s AND social_media = %s
    """, (repost_username, repost_social_media))
    check_user = cursor.fetchone()

    print("Checked the finding user")

    if not check_user:
        cursor.execute("""
            INSERT INTO User (username, social_media, first_name, last_name, country_of_birth, country_of_residence, age, gender, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (repost_username, repost_social_media, None, None, None, None, None, None, None))
        conn.commit()
    print("Finished user")

    print("Checking original post")
    # Check if original post exists
    cursor.execute("""
        SELECT * FROM Post
        WHERE post_username = %s AND post_social_media = %s AND post_time = %s
    """, (original_username, original_social_media, original_post_time))
    check_original_post = cursor.fetchone()

    if not check_original_post:
        flash(f"Original post not found", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('entry'))
    print("Finished original post")

    print("Checking repost exists")
    # Check if repost already exists
    cursor.execute("""
        SELECT * FROM Repost
        WHERE repost_username = %s AND repost_social_media = %s AND repost_time = %s
    """, (repost_username, repost_social_media, repost_time))
    check_repost = cursor.fetchone()

    if not check_repost:
        # Insert repost
        cursor.execute("""
            INSERT INTO Repost (
                original_post_username, original_social_media, original_post_time,
                repost_username, repost_social_media, repost_time,
                repost_location_city, repost_location_state, repost_location_country,
                repost_likes, repost_dislikes, repost_has_multimedia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            original_username, original_social_media, original_post_time,
            repost_username, repost_social_media, repost_time,
            repost_city, repost_state, repost_country,
            repost_likes, repost_dislikes, repost_multimedia
        ))
        conn.commit()

        # Add to post as well
        cursor.execute("""
            INSERT INTO Post (
                post_username, post_social_media, post_time,
                likes, dislikes, location_city, location_state, location_country,
                has_multimedia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            repost_username, repost_social_media, repost_time,
            repost_likes, repost_dislikes, repost_city, repost_state, repost_country,
            repost_multimedia
        ))
        conn.commit()
    else:
        # Update repost
        update_fields = []
        update_values = []

        if repost_city is not None:
            update_fields.append("repost_location_city = %s")
            update_values.append(repost_city)
        if repost_state is not None:
            update_fields.append("repost_location_state = %s")
            update_values.append(repost_state)
        if repost_country is not None:
            update_fields.append("repost_location_country = %s")
            update_values.append(repost_country)
        if repost_likes is not None:
            update_fields.append("repost_likes = %s")
            update_values.append(repost_likes)
        if repost_dislikes is not None:
            update_fields.append("repost_dislikes = %s")
            update_values.append(repost_dislikes)
        if repost_multimedia is not None:
            update_fields.append("repost_has_multimedia = %s")
            update_values.append(repost_multimedia)

        if update_fields:
            update_query = f"""
                UPDATE Repost
                SET {', '.join(update_fields)}
                WHERE repost_username = %s AND repost_social_media = %s AND repost_time = %s
            """
            update_values.extend([repost_username, repost_social_media, repost_time])
            cursor.execute(update_query, tuple(update_values))
            conn.commit()

            add_post(conn, repost_username, repost_social_media, repost_time, None, repost_likes, repost_dislikes,
                     repost_city, repost_state, repost_country, repost_multimedia)
        else:
            flash("Repost already exists", "danger")
            return redirect(url_for('entry'))

    print("Finished insert")
    cursor.close()


def add_project_post(conn, project_name, username, social_media, post_time):
    cursor = conn.cursor()

    # Check if this link already exists
    cursor.execute("""
        SELECT * FROM Project_Post
        WHERE project_name = %s AND post_username = %s AND post_social_media = %s AND post_time = %s
    """, (project_name, username, social_media, post_time))
    check_project_post = cursor.fetchone()

    if check_project_post:
        flash(f"Project Post already exists", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('entry'))
    
    cursor.execute("""
        INSERT INTO Project_Post (project_name, post_username, post_social_media, post_time)
        VALUES (%s, %s, %s, %s)
    """, (project_name, username, social_media, post_time))

    conn.commit()
    cursor.close()

def add_project(conn, project_name):
    cursor = conn.cursor()

    # Check if project exists
    cursor.execute("SELECT name FROM Project WHERE name = %s", (project_name,))
    check_project = cursor.fetchone()

    if not check_project:
        cursor.execute("INSERT INTO Project (name) VALUES (%s)", (project_name,))
        conn.commit()

    cursor.close()

from flask import jsonify, request

@app.route('/posts/add', methods=['POST'])
def add_post_form():
    data = request.get_json()
    print("JSON: ", data)

    project_name = data['project_name'] or None
    user = data['userInfo']
    original = data['originalPost']
    repost = data['repost']

    username = user['username'].strip()
    social_media = user['social_media'].lower().strip()
    first_name = user.get('first_name') or None
    last_name = user.get('last_name') or None
    country_birth = user.get('country_birth').lower() or None
    country_residence = user.get('country_residence').lower() or None
    age = user.get('age') or None
    gender = user.get('gender').lower() or None
    verified = user.get('verified') or None

    post_time_raw = original.get('post_time')
    post_time = post_time_raw.replace('T', ' ') + ":00"
    text = original.get('post_text') or None
    likes = original.get('post_likes') or None
    dislikes = original.get('post_dislikes') or None
    city = original.get('post_city').lower() or None
    state = original.get('post_state').lower() or None
    country = original.get('post_country').lower() or None
    multimedia = original.get('post_multimedia') or None

    repost_username = repost.get('repost_username') or None
    repost_social_media = repost.get('repost_social_media').lower() or None
    repost_time_raw = repost.get('repost_time') or None
    repost_time = None
    if repost_time_raw:
        repost_time = repost_time_raw.replace('T', ' ') + ":00"
    repost_city = repost.get('repost_city').lower() or None
    repost_state = repost.get('repost_state').lower() or None
    repost_country = repost.get('repost_country').lower() or None
    repost_likes = repost.get('repost_likes') or None
    repost_dislikes = repost.get('repost_dislikes') or None
    repost_multimedia = repost.get('repost_multimedia') or None

    if repost_username or repost_social_media or repost_time:
        if not (repost_username and repost_social_media and repost_time):
            return jsonify({"error": "Repost data is incomplete"}), 400
        else:
            repost_time_check = datetime.strptime(repost_time, '%Y-%m-%d %H:%M:%S')
            post_time_check = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
            if repost_time_check <= post_time_check:
                return jsonify({"error": "Repost time cannot be at or before original post time"}), 400

    conn = get_db_connection()
    print("\nHERE")
    if conn:
        cursor = conn.cursor()


        # Add to tables
        add_social_media(conn, social_media)
        add_user(conn, username, social_media, first_name, last_name,
                 country_birth, country_residence, age, gender, verified)
        add_post(conn, username, social_media, post_time, text, likes,
                 dislikes, city, state, country, multimedia)
        if repost_username and repost_social_media and repost_time:
            add_repost(conn, repost_username, repost_social_media, repost_time,
                       repost_city, repost_state, repost_country,
                       repost_likes, repost_dislikes, repost_multimedia,
                       username, social_media, post_time)
            if project_name:
                add_project_post(conn, project_name, repost_username, repost_social_media, repost_time)
        if project_name:
            add_project(conn, project_name)
            add_project_post(conn, project_name, username, social_media, post_time)

        conn.close()
        flash("Post submitted successfully!", "success")
        return jsonify({"message": "Post added successfully"}), 200
    

    return jsonify({"error": "Database connection error"}), 500


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
            
        
            
            return render_template('query_posts_results.html', posts=posts, 
                                  media_name=media_name, start_date=start_date, 
                                  end_date=end_date, username=username, 
                                  first_name=first_name, last_name=last_name)
        
        flash("Database connection error", "danger")
    
    # GET request or failed query
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM social_media")
        social_media = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('query_posts.html', social_media=social_media)
    
    flash("Database connection error", "danger")
    return redirect(url_for('index'))

from flask import jsonify
from datetime import datetime
@app.route('/search-posts', methods=['GET'])
def search_posts():
    try:
        username = request.args.get('username') or None
        media_name_raw = request.args.get('social_media') or None
        media_name = None
        if media_name_raw:
            media_name = media_name_raw.lower()
        start_date = request.args.get('start_date') or None
        end_date = request.args.get('end_date') or None
        # post_time_raw = request.args.get('post_time')
        # post_time = None
        # if post_time_raw:
        #     post_time = post_time_raw.replace('T', ' ') + ":00"
        first_name = request.args.get('first_name') or None
        last_name = request.args.get('last_name') or None

        if start_date:
            start_date_check = datetime.strptime(start_date, "%Y-%m-%d").date()

        if end_date:
            end_date_check = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date and end_date:
            if start_date_check > end_date_check:
                flash("Start date must be before end date", "danger")
                return redirect(url_for('query'))


        query_params = {
            'username': username,
            'social_media': media_name,
            'start_date': start_date,
            'end_date': end_date,
            'first_name': first_name,
            'last_name': last_name
        }

        # Log the incoming parameters to check what's being passed
        print(f"Received parameters - username: {username}, social_media: {media_name}, start_date: {start_date}, end_date: {end_date} first_name: {first_name}, last_name: {last_name}")

        query = """
            SELECT p.text, sm.name AS social_media, u.username, p.post_time
            FROM Post p
            JOIN User u ON p.post_username = u.username AND p.post_social_media = u.social_media
            JOIN Social_Media sm ON p.post_social_media = sm.name
            WHERE 1=1
        """
        params = []

        if media_name:
            query += " AND sm.name = %s"
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

            # Log the results
            print(f"Query results: {posts}")

            if not posts:
                print("POST NOT FOUND")
                return render_template('post_results.html', query=query_params, posts=[])  # Return empty JSON array if no results found

            # Process the posts and include project names
            for post in posts:
                cursor.execute("""
                    SELECT project_name
                    FROM Project_Post
                    WHERE post_username = %s AND post_social_media = %s AND post_time = %s
                """, (post['username'], post['social_media'], post['post_time']))
                projects = cursor.fetchall()
                print(f"PROJECTS for {post['username']}: {projects}")
                post['post_time'] = post['post_time'].strftime('%Y-%m-%d %H:%M:%S')
                post['projects'] = [project['project_name'] for project in projects]

            cursor.close()
            conn.close()

            print("THIS IS BEING RETURNED: ", posts)
            return render_template('post_results.html', query=query_params, posts=posts)


    except Exception as e:
        import traceback
        print("Error in /search-posts route:")
        traceback.print_exc()  # Print the full stack trace for debugging
        return jsonify({'error': str(e)}), 500  # Ensure a response is returned on error


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

# experiment query
@app.route('/experiment_query', methods=['GET', 'POST'])
def experiment_query():
    if request.method == 'POST':
        experiment_name = request.form.get('experiment_name')
        
        if not experiment_name:
            flash('Please enter a project name', 'danger')
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
    else:
        conn = get_db_connection()
        # debug
        if not conn:
            print("❌ DB connection failed")
        if conn:
            print("✅ DB connection success")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT name FROM Project")
            experiments = cursor.fetchall()
            print("🔍 Query results:", experiments, flush=True)
            cursor.close()
            conn.close()
            return render_template('experiment_query.html', experiments=experiments)


def query_experiment(experiment_name):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get project details
            cursor.execute("""
                SELECT name, manager_firstname, manager_lastname, 
                       institute_name, start_date, end_date
                FROM Project 
                WHERE name = %s
            """, (experiment_name,))
            
            project = cursor.fetchone()

            # convert date
            if project and 'start_date' in project and project['start_date']:
                project['start_date'] = str(project['start_date'])
            if project and 'end_date' in project and project['end_date']:
                project['end_date'] = str(project['end_date'])
                
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            # Get fields for this project
            cursor.execute("""
                SELECT field_name
                FROM Field
                WHERE project_name = %s
            """, (experiment_name,))
            
            fields = cursor.fetchall()
            
            # Get posts associated with this project
            cursor.execute("""
                SELECT pp.post_username, pp.post_social_media, pp.post_time,
                       p.text, p.likes, p.dislikes, p.location_city, p.location_state, p.location_country, p.has_multimedia
                FROM Project_Post pp
                JOIN Post p ON pp.post_username = p.post_username 
                               AND pp.post_social_media = p.post_social_media
                               AND pp.post_time = p.post_time
                WHERE pp.project_name = %s
            """, (experiment_name,))
            
            posts = cursor.fetchall()
            
            # Get analysis results for each post
            for post in posts:
                cursor.execute("""
                    SELECT field_name, analysis
                    FROM Analysis_Result
                    WHERE project_name = %s 
                      AND post_username = %s
                      AND post_social_media = %s
                      AND post_time = %s
                """, (experiment_name, post['post_username'], post['post_social_media'], post['post_time']))
                
                results = cursor.fetchall()
                post['results'] = {result['field_name']: result['analysis'] for result in results}
            
            # Calculate field statistics
            field_stats = {}
            for field in fields:
                field_name = field['field_name']
                field_stats[field_name] = {'total': len(posts), 'filled': 0}
                
                for post in posts:
                    if field_name in post.get('results', {}) and post['results'][field_name]:
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

if __name__ == '__main__':
    app.run(debug=True)