from flask import Flask, redirect, render_template, url_for, make_response, send_from_directory, request
import database
import html
import secrets
import datetime
import bcrypt

app = Flask(__name__)


@app.route('/<path:path>')
def send_static(path):
    response = make_response(send_from_directory('static', path), 200)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/')
def index():
    token = request.cookies.get('auth', None)
    if token and database.check_token(token):
        response = make_response(
            redirect(url_for('dashboard', _external=True)))
        response.set_cookie('auth', token)
        return response
    return render_template('pages/index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Check if user is already logged in
    token = request.cookies.get('auth', None)
    if token is not None and database.check_token(token):
        response = make_response(
            redirect(url_for('dashboard', _external=True)))
        response.set_cookie('auth', token)
        return response

    # Handle login form submission
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username:
            error = 'Username Empty'
        elif not password:
            error = 'Password Empty'
        else:
            username = html.escape(username)
            user = database.get_user_by_username(username)
            if user is None:
                error = 'No User Found'
            else:
                # Verify password
                ph = bcrypt.hashpw(password.encode(), user.salt)
                if ph == user.passhash:
                    token = secrets.token_hex()
                    database.set_user_token(
                        username, token, datetime.datetime.now(
                            tz=datetime.timezone.utc)
                    )
                    response = make_response(
                        redirect(url_for('dashboard', _external=True)))
                    response.set_cookie('auth', token)
                    return response
                else:
                    error = 'Password Incorrect'

        # If there's an error, render the index page with the error message
        response = make_response(render_template(
            '/pages/index.html', error=error))
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    # For GET requests, render the index page with no error
    response = make_response(render_template('/pages/index.html', error=''))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # Checks if the user is signed in
    token = request.cookies.get('auth', None)
    if token is not None and database.check_token(token=token):
        response = make_response(redirect(url_for('index', _external=True)))
        response.set_cookie('auth', token)
        return response

    # If the user is requesting the signup form
    if request.method == 'GET':
        response = make_response(render_template(
            'pages/signUp.html', error='', login=login), 200)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    # Handle signup form submission
    else:
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        email = request.form.get('email', None)
        password_confirm = request.form.get('password_confirm', None)
        major = request.form.get('major', None)

        departments = request.form.getlist('department[]')
        course_numbers = request.form.getlist('course_number[]')
        semester = request.form.getlist('semester')

        # classes dictionary
        classes = {}
        for dept, course in zip(departments, course_numbers):
            if dept in classes:
                classes[dept].append(course)
            else:
                classes[dept] = [course]

        # Error handling
        if password != password_confirm or not password:
            print("whoops 4")
            error = "Password empty or do not match"
            response = make_response(render_template(
                'pages/signUp.html', error=error, login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response

        if not username or username.strip() == '':
            error = "Username Field Empty"
            response = make_response(render_template(
                'pages/signUp.html', error=error, login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response

        if not email or "@u.rochester.edu" not in email:
            error = "You are not a student"
            response = make_response(render_template(
                'pages/signUp.html', error=error, login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response

        if not major:
            error = "how did you even do this you bastard"
            response = make_response(render_template(
                'pages/signUp.html', error=error, login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response

        # Escape and add user to database
        username = html.escape(username)
        if database.add_user(username, password, email, major, classes, semester):
            print("added apparently")
            token = secrets.token_hex()
            database.set_user_token(
                username, token, datetime.datetime.now(tz=datetime.timezone.utc))
            response = make_response(
                redirect(url_for('index', _external=True)))
            response.set_cookie('auth', token)
            return response
        else:
            error = "Username Already Exists"
            response = make_response(render_template(
                'pages/signUp.html', error=error, login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response


@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('auth', None)
    if (token != None and database.check_token(token=token)):
        user = database.get_user_by_token(token=token)
        return render_template('/pages/dashBoard.html', username=user.username)
    else:
        response = make_response(redirect(url_for('index', _external=True)))
        response.set_cookie('auth', '', max_age=0)
        return response


@app.route('/profile')
def profile():
    token = request.cookies.get('auth', None)
    if (token != None and database.check_token(token=token)):
        user = database.get_user_by_token(token=token)
        return render_template('/pages/profile.html')
    else:
        response = make_response(redirect(url_for('index', _external=True)))
        response.set_cookie('auth', '', max_age=0)
        return response


@app.route('/schedulebuilder', methods=['POST', 'GET'])
def schedulebuilder():
    token = request.cookies.get('auth', None)
    if token is None or not database.check_token(token=token):
        response = make_response(redirect(url_for('index', _external=True)))
        response.set_cookie('auth', '', max_age=0)
        return response
    else:
        if request.method == 'GET':
            schedule = {}
            return render_template('pages/scheduleBuilder.html', schedule=schedule)
        else:
            user = database.get_user_by_token(token=token)
            username = user.username
            goals = request.form.get("goals")

            # Your existing code to process goals and generate the schedule
            # For now, we'll use dummy data
            dummy_data = {
                7: ["CSC 459-1", "CSC 477-01", "CSC 445-01"],
                8: ["CSC 480-1", "CSC 482-01", "CSC 551-01", "CSC 484-1"]
            }

            # Map semester keys
            semester_map = {
                1: "Freshman Fall", 2: "Freshman Spring",
                3: "Sophomore Fall", 4: "Sophomore Spring",
                5: "Junior Fall", 6: "Junior Spring",
                7: "Senior Fall", 8: "Senior Spring"
            }

            schedule = {}
            for key, classes_list in dummy_data.items():
                semester = semester_map[key]
                schedule[semester] = []
                for cls in classes_list:
                    # Assuming cls is like "CSC 171-1"
                    dept_course = cls.split(" ")[0]  # "CSC"
                    course_section = cls.split(" ")[1]  # "171-1"
                    course_number = course_section.split('-')[0]  # "171"

                    # Fetch class information
                    course_info = database.get_class_info(
                        dept_course, course_number)
                    schedule[semester].append(course_info)

            return render_template('pages/scheduleBuilder.html', schedule=schedule)


app.run(debug=True, host='127.0.0.1', port=8080)
