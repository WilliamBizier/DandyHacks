# Write Wrapper Functions for the database in this file
from pymongo import MongoClient
import bcrypt
import datetime
from hashlib import sha256
from bson.objectid import ObjectId
import random
import string

mongo_client = MongoClient("localhost", 27017)
db = mongo_client["GigaClassGen"]
users = db['users']


class user:
    def __init__(self, user_obj):
        self.username = user_obj['username']
        self.email = user_obj['email']
        self.passhash = user_obj['passhash']
        self.salt = user_obj['salt']
        self.id = user_obj['_id']
        self.token = user_obj['token']
        self.token_date = user_obj['token_date']
        self.classes = user_obj['classes']
        self.socials = user_obj['socials']



# users -> {username:username,passhash:passwordhash,salt:passwordsalt,_id:user_id,token,exp_date}

# all users are students
def add_user(username, password, email):
    check = users.find_one({'username': username})
    if check is not None:
        return False  # Username already exists
    else:
        salt = bcrypt.gensalt()
        passhash = bcrypt.hashpw(password.encode('utf-8'), salt)
        users.insert_one({
            'username': username,
            'email': email,
            'passhash': passhash,
            'salt': salt,
            'token': '',
            'token_date': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'classes': [],
            'socials': []
        })
        return True


# gets the user by their id and returns a user object if found or none if not
def get_user_by_id(id):
    user_found = users.find_one({'_id': ObjectId(id)})
    if (user_found != None):
        return user(user_found)
    else:
        return None

# Gets a users id from their username


def get_id_by_username(username):
    user_found = users.find_one({'username': username})
    if (user_found != None):
        return user_found['_id']
    else:
        return None

# Gets a users username from their id


def get_username_by_id(id):
    user_found = users.find_one({'_id': ObjectId(id)})
    if (user_found != None):
        return user_found['username']
    else:
        return None


def user_delete_by_id(id):
    return users.delete_one({'_id': ObjectId(id)})


def set_user_token(username, token, date=datetime.datetime.now()):
    hash = sha256(token.encode('utf-8')).hexdigest()
    return users.update_many({'username': username}, {"$set": {'token': str(hash), "token_date": date}})


def get_user_by_token(token):
    hash = sha256(token.encode('utf-8')).hexdigest()
    u = users.find_one({'token': hash})
    if u != None:
        return user(u)
    else:
        return None

# Gets the user and returns a user object if found or none if not using the users username


def get_user_by_username(username):
    user_found = users.find_one({'username': username})
    if (user_found != None):
        return user(user_found)
    else:
        return None


def check_username_exists(username):
    test = users.find_one({'username': username})
    if (test == None):
        return False
    else:
        return True


def check_token(token):
    hash = sha256(token.encode('utf-8')).hexdigest()
    u = users.find_one({'token': hash})
    if u != None:
        if token == 'expired':
            # remove token
            return False
        else:
            return True
    else:
        return False


# users.insert_one({
#     'username': 'test_user',
#     'email': 'test@example.com',
#     'passhash': 'dummyhash',
#     'salt': 'dummysalt',
#     'token': '',
#     'token_date': datetime.datetime.utcnow(),
#     'classes': []
# })
# print("Manual user inserted.")
