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
        self.major = user_obj['major']
        self.goals = user_obj['goals']
        self.socials = user_obj['socials']


class classes:
    def __init__(self, class_obj):
        self.id = class_obj['_id']
        self.department = class_obj['department']
        self.course_code = class_obj['course_code']
        self.name = class_obj['name']
        self.professor = class_obj['professor']
        self.day = class_obj['day']
        self.credits = class_obj['credits']
        self.prereqs = class_obj['prereqs']
        self.startDate = class_obj['startDate']
        self.endDate = class_obj['endDate']
        self.term = class_obj['term']


# users -> {username:username,passhash:passwordhash,salt:passwordsalt,_id:user_id,token,exp_date}

# all users are students
def add_user(username, password, email, major, classes):
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
            'classes': classes,
            'major': major,
            'goals': "",
            'socials': {}
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


def getUserClassesLeft(username):
    # Define a sample curriculum for Computer Science
    required_classes_cs = {
        "Computer Science": [
            "CS101", "CS102", "CS201", "CS202",
            "CS301", "CS302", "CS401", "CS402"
        ]
    }

    # valiud user check
    user = users.find_one({'username': username})
    if user is None:
        return False

    major = user['major']
    classes_taken = user['classes']
    print(classes_taken)

    if major == "Computer Science":
        # Required classes for Computer Science major
        CS_classReq = ["171", "172", "173", "242", "252", "254", "280", "282"]
        totalCustom = 13  # Total number of custom classes allowed
        requiredClasses = []
        customClasses = []

        # Check the CSE department first
        if 'CSE' in classes_taken:
            taken_CSE = classes_taken['CSE']

            # Find missing required classes
            missing_classes = [
                cls for cls in CS_classReq if cls not in taken_CSE]
            requiredClasses.extend(missing_classes)

            # Calculate excess classes beyond required ones
            extra_classes = [
                cls for cls in taken_CSE if cls not in CS_classReq]
            totalCustom = totalCustom - len(extra_classes)

            return extra_classes, totalCustom

        else:
            # If no CSE classes are taken
            return CS_classReq[:], totalCustom

    else:
        return False


print(getUserClassesLeft("BallSack"))


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



def process_and_insert_classes(csv_file_path, db):
    import pandas as pd

    # Load the CSV file
    data = pd.read_csv(csv_file_path)
    
    # Reference to the classes collection
    classes_collection = db['classes']
    
    for _, row in data.iterrows():
        # Split the 'Code' column into department and course number
        code = row['Code'].strip()
        dpt, course_number = code.split(' ')[0], code.split(' ')[1].split('-')[0]
        
        # Process the 'Prereqs' into a dictionary
        prereq_raw = str(row['Prereqs']).strip()
        prereqs_dict = {}
        if prereq_raw and prereq_raw != 'nan':
            prereq_list = prereq_raw.split(',')
            for prereq in prereq_list:
                prereq_dpt, prereq_num = prereq.strip().split(' ')[0], prereq.strip().split(' ')[1]
                if prereq_dpt not in prereqs_dict:
                    prereqs_dict[prereq_dpt] = []
                prereqs_dict[prereq_dpt].append(prereq_num)

        # Construct the class document to insert
        class_document = {
            "department": dpt,
            "course_number": course_number,
            "title": row['Title'],
            "credits": row['Credits'],
            "start_time": row['Begin'],
            "end_time": row['End'],
            "term": row['Term'],
            "professor": row['professor'],
            "prereqs": prereqs_dict
        }
        
        # Insert into the database
        classes_collection.insert_one(class_document)
