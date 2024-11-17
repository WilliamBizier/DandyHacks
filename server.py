from flask import Flask,redirect,render_template,url_for,make_response,send_from_directory,request
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
    if (token != None and database.check_token(token)):
        response = make_response(
            redirect(url_for('dashboard', _external=True)))
        response.set_cookie('auth', token)
        return response
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    # check if users logged in, if yes redirect to feed
    token = request.cookies.get('auth', None)
    if (token != None and database.check_token(token)):
        response = make_response(redirect(url_for('index', _external=True)))
        response.set_cookie('auth', token)
        return response
    # if the user is requesting the login form
    if request.method == 'GET':
        response = make_response(render_template('login.html', error=''), 200)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    # submitting login form
    else:
        username = request.form.get('username', None)
        if username != None and username != '' and username != ' ':
            username = html.escape(username)
        else:
            response = make_response(render_template(
                'login.html', error='Username Empty'), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response
        password = request.form.get('password')
        if (password == None or password == ''):
            response = make_response(render_template(
                'login.html', error='password empty'), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response
        user = database.get_user_by_username(username)
        if (user == None):
            response = make_response(render_template(
                'login.html', error='No User Found'), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response
        else:
            # Login has all info needed just need to check password hash
            ph = bcrypt.hashpw(password.encode(), user.salt)
            if ph == user.passhash:
                token = secrets.token_hex()
                database.set_user_token(
                    username, token, datetime.datetime.now(tz=datetime.timezone.utc))
                response = make_response(
                    redirect(url_for('index', _external=True)))
                response.set_cookie('auth', token)
                return response
            response = make_response(render_template(
                'login.html', error='Password Incorrect', login=login), 200)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            return response


    
    