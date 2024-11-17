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
classes_collection = db['classes']



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
        self.semester = user_obj['semester']


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
def add_user(username, password, email, major, classes, semester):
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
            'semester': semester[0],
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
    # Validate if the user exists
    user = users.find_one({'username': username})
    if user is None:
        return False

    major = user['major']
    classes_taken = user['classes']  # Example: {'CSC': ['171', '172'], 'ECON': ['101']}
    print(classes_taken)

    if major == "Computer Science":
        # List of required CS classes
        CS_classReq = ["171", "172", "173", "242", "252", "254", "280", "282"]
        totalCustom = 13  # Total custom classes allowed
        
        # Dictionaries to hold classes categorized by term
        requiredClasses = {"fall": [], "spring": []}
        customClasses = {"fall": [], "spring": []}

        # Use the correct collection to find required classes
        required_classes_cursor = classes_collection.find({'department': 'CSC'})
        required_classes = list(required_classes_cursor)

        # Identify missing required classes
        missing_required = [
            cls for cls in required_classes
            if cls['course_number'] not in classes_taken.get('CSC', [])
        ]

        # Organize missing required classes by term
        for cls in missing_required:
            term = cls.get('term', '').lower()  # e.g., "fall" or "spring"
            if term in requiredClasses:
                requiredClasses[term].append(cls)

        # Identify eligible custom classes
        for cls in required_classes:
            prereqs_met = all(
                prereq_num in classes_taken.get(prereq_dept, [])
                for prereq_dept, prereq_nums in cls['prereqs'].items()
                for prereq_num in prereq_nums
            )
            if prereqs_met and cls['course_number'] not in classes_taken.get('CSC', []):
                term = cls.get('term', '').lower()  # e.g., "fall" or "spring"
                if term in customClasses:
                    customClasses[term].append(cls)

        # Identify extra CSC courses beyond the required ones
        extra_classes = [
            cls for cls in classes_taken.get('CSC', [])
            if cls not in CS_classReq
        ]

        # Calculate the remaining custom class slots
        remaining_custom_slots = totalCustom - len(extra_classes)

        return requiredClasses, customClasses, remaining_custom_slots

    else:
        return False


print(getUserClassesLeft("1"))

def get_class_info(dept, course_number):
    """
    Fetch class information from the database.
    """
    class_info = classes_collection.find_one({
        'department': dept,
        'course_number': course_number
    })

    if class_info:
        return {
            "name": f"{class_info['department']} {class_info['course_number']}",
            "score": class_info.get('credits', 'N/A'),
            "professor": class_info.get('professor', 'N/A'),
            "ranking": "N/A",  # Replace with actual data if available
            "difficulty": "N/A",  # Replace with actual data if available
            "wta": "N/A",  # Replace with actual data if available
            "start": class_info.get('start_time', 'N/A'),
            "end": class_info.get('end_time', 'N/A'),
            "term": class_info.get('term', 'N/A')
        }
    else:
        return {
            "name": f"{dept} {course_number}",
            "score": "N/A",
            "professor": "N/A",
            "ranking": "N/A",
            "difficulty": "N/A",
            "wta": "N/A",
            "start": "N/A",
            "end": "N/A",
            "term": "N/A"
        }



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


# this is used to get the CSV into the DB


# def process_and_insert_classes(csv_file_path, db):
#     import pandas as pd

#     # Load the CSV file
#     data = pd.read_csv(csv_file_path)
    
#     # Reference to the classes collection
#     classes_collection = db['classes']
    
#     for _, row in data.iterrows():
#         # Split the 'Code' column into department and course number
#         code = row['Code'].strip()
#         dpt, course_number = code.split(' ')[0], code.split(' ')[1].split('-')[0]
        
#         # Process the 'Prereqs' into a dictionary
#         prereq_raw = str(row['Prereqs']).strip()
#         prereqs_dict = {}
#         if prereq_raw and prereq_raw != 'nan':
#             prereq_list = prereq_raw.split(',')
#             for prereq in prereq_list:
#                 prereq_dpt, prereq_num = prereq.strip().split(' ')[0], prereq.strip().split(' ')[1]
#                 if prereq_dpt not in prereqs_dict:
#                     prereqs_dict[prereq_dpt] = []
#                 prereqs_dict[prereq_dpt].append(prereq_num)

#         # Handle missing columns safely
#         class_document = {
#             "department": dpt,
#             "course_number": course_number,
#             "title": row['Title'],
#             "credits": row['Credits'],
#             "start_time": row.get('Begin', 'N/A'),  # Default to 'N/A' if missing
#             "end_time": row.get('End', 'N/A'),      # Default to 'N/A' if missing
#             "term": row.get('Term', 'N/A'),         # Default to 'N/A' if missing
#             "professor": row.get('professor', 'N/A'),  # Handle missing professor
#             "prereqs": prereqs_dict
#         }
        
#         # Insert into the database
#         try:
#             classes_collection.insert_one(class_document)
#         except Exception as e:
#             print(f"Error inserting document: {e}")

        
# process_and_insert_classes("courses_lectures.csv", db)