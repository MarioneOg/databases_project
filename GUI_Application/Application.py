from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import datetime

app = Flask(__name__)
app.secret_key = 'social_media_analysis_key'

# # Database Configuration
# @app.route('/connect-db', methods=['POST'])
# def get_db_config():
#     # import mysql.connector

#     try:
#         # Establish connection
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="myuser",
#             password="mypassword",
#             database="social_media_analysis"
#         )   
#         if conn.is_connected():
#             print("Connected to the database successfully!")
#         else:
#             print("Connection failed.")
    
#         # Close the connection
#         conn.close()

#     except mysql.connector.Error as err:
#         print(f"Error: {err}")


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
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                conn.close()
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
def post_results():
    query = request.args.to_dict()
    return render_template('post_results.html', query=query)

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

# @app.route('/social_media/add', methods=['GET', 'POST'])
# def add_social_media():
#     if request.method == 'POST':
#         media_name = request.form['media_name']
        
#         conn = get_db_connection()
#         if conn:
#             cursor = conn.cursor()
#             try:
#                 cursor.execute("INSERT INTO social_media (media_name) VALUES (%s)", (media_name,))
#                 conn.commit()
#                 flash(f"Social media '{media_name}' added successfully", "success")
#             except Error as e:
#                 flash(f"Error adding social media: {e}", "danger")
            
#             cursor.close()
#             conn.close()
#             return redirect(url_for('list_social_media'))
        
#         flash("Database connection error", "danger")
    
#     return render_template('add_social_media.html')

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
def add_project_form():
    if request.method == 'POST':
        project_name = request.form['project_name']
        manager_first_name = request.form['manager_first_name'] or None
        manager_last_name = request.form['manager_last_name'] or None
        institute_name = request.form['institute_name'] or None
        start_date = request.form['start_date'] or None
        end_date = request.form['end_date'] or None
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if institute exists
            if institute_name:
                cursor.execute("SELECT name FROM Institute WHERE name = %s", (institute_name,))
                institute = cursor.fetchone()
            
                if not institute:
                    # Create institute
                    cursor.execute("INSERT INTO Institute (name) VALUES (%s)", (institute_name,))
                    # institute_id = cursor.lastrowid
                else:
                    cursor.execute("UPDATE Institute SET name = (%s)", (institute_name,))
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
                cursor.execute("""
                    UPDATE Project 
                    SET manager_firstname = (%s), manager_lastname = (%s), 
                               institute_name = (%s), start_date = (%s), end_date = (%s)
                    WHERE name = %s
                """, (manager_first_name, manager_last_name, 
                institute_name, start_date, end_date, project_name))
                conn.commit()
            # project_id = cursor.lastrowid
            
            # Handle project fields
            # field_names = request.form.getlist('field_name')
            # for field_name in field_names:
            #     if field_name.strip():
            #         cursor.execute("""
            #             INSERT INTO project_fields (project_id, field_name)
            #             VALUES (%s, %s)
            #         """, (project_id, field_name))
            
            # conn.commit()
            cursor.close()
            conn.close()
            
            flash("Project added successfully", "success")
            return redirect(url_for('entry'))
        
        flash("Database connection error", "danger")

    
    # # GET request
    # else:
    #     conn = get_db_connection()
    #     if conn:
    #         cursor = conn.cursor(dictionary=True)
    #         cursor.execute("SELECT name FROM Institute")
    #         institutes = cursor.fetchall()
    #         cursor.close()
    #         conn.close()
    #         # return render_template('entry.html', institutes=institutes)
    
    #     flash("Database connection error", "danger")
    #     return redirect(url_for('index'))
        
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
        project_name = request.form['project_name']
        username = request.form['username']
        social_media = request.form['social_media'] 
        post_time = request.form['post_time'] 
        field_name = request.form['field_name'] 
        analysis = request.form['analysis'] or None

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            project = find_project(conn, project_name)
            user = find_user(conn, username, social_media)
            post = find_post(conn, username, social_media, post_time)

            if project and user and post:
                # Add field
                add_field(conn, field_name, project_name)
                
                # Add analysis
                add_analysis(conn, project_name, username, social_media, post_time, field_name, analysis)

                flash("Analysis added successfully", "success")
                return redirect(url_for('entry'))
            else:
                flash("Project, user, or post not found", "danger")
                return redirect(url_for('entry'))

            # # Check if analysis exists
            # cursor.execute("""
            #     SELECT * FROM Analysis
            #     WHERE project_name = %s AND post_username = %s AND post_social_media = %s AND post_time = %s AND field_name = %s
            # """, (project_name, username, social_media, post_time, field_name))
            # check_analysis = cursor.fetchone()

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

# @app.route('/users/add', methods=['GET', 'POST'])
# def add_user():
#     if request.method == 'POST':
#         media_name = request.form['media_name']
#         username = request.form['username']
#         first_name = request.form['first_name'] or None
#         last_name = request.form['last_name'] or None
#         country_of_birth = request.form['country_of_birth'] or None
#         country_of_residence = request.form['country_of_residence'] or None
#         age = request.form['age'] or None
#         gender = request.form['gender'] or None
#         is_verified = 'is_verified' in request.form
        
#         conn = get_db_connection()
#         if conn:
#             cursor = conn.cursor()
            
#             # Check if social media exists
#             cursor.execute("SELECT media_id FROM social_media WHERE media_name = %s", (media_name,))
#             media = cursor.fetchone()
            
#             if not media:
#                 # Create social media
#                 cursor.execute("INSERT INTO social_media (media_name) VALUES (%s)", (media_name,))
#                 media_id = cursor.lastrowid
#             else:
#                 media_id = media[0]
            
#             # Create user
#             try:
#                 cursor.execute("""
#                     INSERT INTO users (media_id, username, first_name, last_name, 
#                                      country_of_birth, country_of_residence, age, 
#                                      gender, is_verified)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (media_id, username, first_name, last_name, 
#                      country_of_birth, country_of_residence, age, 
#                      gender, is_verified))
                
#                 conn.commit()
#                 flash("User added successfully", "success")
#             except Error as e:
#                 flash(f"Error adding user: {e}", "danger")
            
#             cursor.close()
#             conn.close()
#             return redirect(url_for('list_users'))
        
#         flash("Database connection error", "danger")
    
#     # GET request
#     conn = get_db_connection()
#     if conn:
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT media_name FROM social_media")
#         social_media = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return render_template('add_user.html', social_media=social_media)
    
#     flash("Database connection error", "danger")
#     return redirect(url_for('index'))

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
    else:
        cursor.execute("UPDATE Social_Media SET name = (%s)", (social_media,))
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

    if check_repost:
        flash(f"Repost already exists", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('entry'))
    print("Finished repost exists")

    # Insert repost
    print("Inserting now")
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



@app.route('/posts/add', methods=['GET', 'POST'])
def add_post_form():
    if request.method == 'POST':
        project_name = request.form['project_name']

        username = request.form['username']
        social_media = request.form['social_media']
        first_name = request.form['first_name'] or None
        last_name = request.form['last_name'] or None
        country_birth = request.form['country_birth'] or None
        country_residence = request.form['country_residence'] or None
        age = request.form['age'] or None
        gender = request.form['gender'] or None
        verified = request.form['verified'] or None

        post_time_raw = request.form['post_time']
        post_time = post_time_raw.replace('T', ' ') + ":00"
        text = request.form['text'] or None
        likes = request.form['likes'] or None
        dislikes = request.form['dislikes'] or None
        city = request.form['city'] or None
        state = request.form['state'] or None
        country = request.form['country'] or None
        multimedia = request.form['multimedia'] or None

        repost_username = request.form['repost_username'] or None
        repost_social_media = request.form['repost_social_media'] or None
        repost_time_raw = request.form['repost_time'] or None
        if repost_time_raw:
            repost_time = post_time_raw.replace('T', ' ') + ":00"
        repost_city = request.form['repost_city'] or None
        repost_state = request.form['repost_state'] or None
        repost_country = request.form['repost_country'] or None
        repost_likes = request.form['repost_likes'] or None
        repost_dislikes = request.form['repost_dislikes'] or None
        repost_multimedia = request.form['repost_multimedia'] or None

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            
            # Check if project exists
            cursor.execute("SELECT name FROM Project WHERE name = %s", (project_name,))
            check_project = cursor.fetchone()
            
            if not check_project:
                flash(f"Project {project_name} not found", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for('entry'))
            # else:
            #     institute_id = institute[0]
            
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
            add_project_post(conn, project_name, username, social_media, post_time)
            

            conn.close()
            
            flash("Post added successfully", "success")
            return redirect(url_for('entry'))
        
        flash("Database connection error", "danger")



    # if request.method == 'POST':
    #     media_name = request.form['media_name']
    #     username = request.form['username']
    #     post_text = request.form['post_text']
    #     post_time = request.form['post_time']
    #     city = request.form['city'] or None
    #     state = request.form['state'] or None
    #     country = request.form['country'] or None
    #     likes = request.form['likes'] or 0
    #     dislikes = request.form['dislikes'] or 0
    #     has_multimedia = 'has_multimedia' in request.form
        
    #     conn = get_db_connection()
    #     if conn:
    #         cursor = conn.cursor()
            
    #         # Get user ID
    #         cursor.execute("""
    #             SELECT u.user_id, sm.media_id FROM users u
    #             JOIN social_media sm ON u.media_id = sm.media_id
    #             WHERE sm.media_name = %s AND u.username = %s
    #         """, (media_name, username))
    #         user_info = cursor.fetchone()
            
    #         if not user_info:
    #             flash(f"User {username} on {media_name} not found", "danger")
    #             cursor.close()
    #             conn.close()
    #             return redirect(url_for('add_post'))
            
    #         user_id, media_id = user_info
            
    #         # Check if post already exists
    #         cursor.execute("""
    #             SELECT post_id FROM posts 
    #             WHERE user_id = %s AND media_id = %s AND post_time = %s
    #         """, (user_id, media_id, post_time))
    #         existing_post = cursor.fetchone()
            
    #         if existing_post:
    #             flash(f"Post already exists with ID {existing_post[0]}", "warning")
    #             post_id = existing_post[0]
    #         else:
    #             # Create post
    #             cursor.execute("""
    #                 INSERT INTO posts (user_id, media_id, post_text, post_time, city, state, 
    #                                  country, likes, dislikes, has_multimedia)
    #                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """, (user_id, media_id, post_text, post_time, city, state, 
    #                  country, likes, dislikes, has_multimedia))
                
    #             conn.commit()
    #             post_id = cursor.lastrowid
    #             flash("Post added successfully", "success")
            
    #         # Check if we need to associate with a project
    #         if 'project_id' in request.form and request.form['project_id']:
    #             project_id = request.form['project_id']
                
    #             # Check if association already exists
    #             cursor.execute("""
    #                 SELECT 1 FROM project_posts 
    #                 WHERE project_id = %s AND post_id = %s
    #             """, (project_id, post_id))
    #             if not cursor.fetchone():
    #                 cursor.execute("""
    #                     INSERT INTO project_posts (project_id, post_id)
    #                     VALUES (%s, %s)
    #                 """, (project_id, post_id))
    #                 conn.commit()
    #                 flash("Post associated with project", "success")
            
    #         cursor.close()
    #         conn.close()
    #         return redirect(url_for('list_posts'))
        
    #     flash("Database connection error", "danger")
    
    # # GET request
    # conn = get_db_connection()
    # if conn:
    #     cursor = conn.cursor(dictionary=True)
    #     cursor.execute("""
    #         SELECT u.username, sm.media_name
    #         FROM users u
    #         JOIN social_media sm ON u.media_id = sm.media_id
    #     """)
    #     users = cursor.fetchall()
        
    #     cursor.execute("SELECT project_id, project_name FROM projects")
    #     projects = cursor.fetchall()
        
    #     cursor.close()
    #     conn.close()
    #     return render_template('add_post.html', users=users, projects=projects)
    
    # flash("Database connection error", "danger")
    # return redirect(url_for('index'))

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

# @app.route('/posts/repost', methods=['GET', 'POST'])
# def add_repost():
#     post_id = request.form['post_id']
#     media_name = request.form['media_name']
#     username = request.form['username']
#     repost_time = request.form['repost_time']
    
#     conn = get_db_connection()
#     if conn:
#         cursor = conn.cursor()
        
#         # Get user ID
#         cursor.execute("""
#             SELECT user_id FROM users u
#             JOIN social_media sm ON u.media_id = sm.media_id
#             WHERE sm.media_name = %s AND u.username = %s
#         """, (media_name, username))
#         user_result = cursor.fetchone()
        
#         if not user_result:
#             flash(f"User {username} on {media_name} not found", "danger")
#             cursor.close()
#             conn.close()
#             return redirect(url_for('view_post', post_id=post_id))
        
#         user_id = user_result[0]
        
#         # Add repost
#         cursor.execute("""
#             INSERT INTO reposts (post_id, user_id, repost_time)
#             VALUES (%s, %s, %s)
#         """, (post_id, user_id, repost_time))
        
#         conn.commit()
#         cursor.close()
#         conn.close()
        
#         flash("Repost added successfully", "success")
#         return redirect(url_for('view_post', post_id=post_id))
    
#     flash("Database connection error", "danger")
#     return redirect(url_for('view_post', post_id=post_id))

# Analysis Results
# @app.route('/analysis/add', methods=['GET', 'POST'])
# def add_analysis():
#     if request.method == 'POST':
#         project_id = request.form['project_id']
#         post_id = request.form['post_id']
        
#         conn = get_db_connection()
#         if conn:
#             cursor = conn.cursor()
            
#             # Get all fields for the project
#             cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project_id,))
#             project_fields = cursor.fetchall()
            
#             # Check if post is associated with project
#             cursor.execute("SELECT 1 FROM project_posts WHERE project_id = %s AND post_id = %s", (project_id, post_id))
#             if not cursor.fetchone():
#                 # Associate post with project
#                 cursor.execute("INSERT INTO project_posts (project_id, post_id) VALUES (%s, %s)", (project_id, post_id))
#                 conn.commit()
            
#             # Process field values
#             for field_id, field_name in project_fields:
#                 field_key = f"field_{field_id}"
#                 if field_key in request.form:
#                     result_value = request.form[field_key]
                    
#                     # Check if result already exists
#                     cursor.execute("""
#                         SELECT result_id FROM analysis_results 
#                         WHERE project_id = %s AND post_id = %s AND field_id = %s
#                     """, (project_id, post_id, field_id))
#                     existing_result = cursor.fetchone()
                    
#                     if existing_result:
#                         # Update existing result
#                         cursor.execute("""
#                             UPDATE analysis_results SET result_value = %s
#                             WHERE project_id = %s AND post_id = %s AND field_id = %s
#                         """, (result_value, project_id, post_id, field_id))
#                     else:
#                         # Create new result
#                         cursor.execute("""
#                             INSERT INTO analysis_results (project_id, post_id, field_id, result_value)
#                             VALUES (%s, %s, %s, %s)
#                         """, (project_id, post_id, field_id, result_value))
            
#             conn.commit()
#             cursor.close()
#             conn.close()
            
#             flash("Analysis results saved successfully", "success")
#             return redirect(url_for('view_project', project_id=project_id))
        
#         flash("Database connection error", "danger")
    
#     # GET request
#     project_id = request.args.get('project_id')
#     post_id = request.args.get('post_id')
    
#     if not project_id or not post_id:
#         flash("Missing project or post information", "danger")
#         return redirect(url_for('index'))
    
#     conn = get_db_connection()
#     if conn:
#         cursor = conn.cursor(dictionary=True)
        
#         # Get project details
#         cursor.execute("SELECT project_id, project_name FROM projects WHERE project_id = %s", (project_id,))
#         project = cursor.fetchone()
        
#         if not project:
#             flash("Project not found", "danger")
#             cursor.close()
#             conn.close()
#             return redirect(url_for('index'))
        
#         # Get post details
#         cursor.execute("""
#             SELECT p.post_id, p.post_text, sm.media_name, u.username, p.post_time
#             FROM posts p
#             JOIN users u ON p.user_id = u.user_id
#             JOIN social_media sm ON p.media_id = sm.media_id
#             WHERE p.post_id = %s
#         """, (post_id,))
#         post = cursor.fetchone()
        
#         if not post:
#             flash("Post not found", "danger")
#             cursor.close()
#             conn.close()
#             return redirect(url_for('view_project', project_id=project_id))
        
#         # Get fields for this project
#         cursor.execute("SELECT field_id, field_name FROM project_fields WHERE project_id = %s", (project_id,))
#         fields = cursor.fetchall()
        
#         # Get existing results
#         cursor.execute("""
#             SELECT field_id, result_value
#             FROM analysis_results
#             WHERE project_id = %s AND post_id = %s
#         """, (project_id, post_id))
#         existing_results = {result['field_id']: result['result_value'] for result in cursor.fetchall()}

#         cursor.close()
#         conn.close()
        
#         return render_template('add_analysis.html', project=project, post=post, 
#                                fields=fields, existing_results=existing_results)
    
#     flash("Database connection error", "danger")
#     return redirect(url_for('index'))

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
    post_time = request.args.get('postTime')  # e.g. '2024-05-04T15:30'
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

    if post_time:
        try:
            # MySQL expects 'YYYY-MM-DD HH:MM:SS'
            parsed_time = datetime.strptime(post_time, "%Y-%m-%dT%H:%M")
            query += " AND p.post_time = %s"
            params.append(parsed_time.strftime("%Y-%m-%d %H:%M:%S"))
        except ValueError:
            return jsonify({'error': 'Invalid date format for postTime'}), 400

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