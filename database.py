#Write Wrapper Functions for the database in this file
from pymongo import MongoClient
import bcrypt
import datetime
from hashlib import sha256
from bson.objectid import ObjectId
import random
import string

mongo_client = MongoClient("localhost")
db = mongo_client["GigaClassGen"]
users = db['users']
classrooms = db['classrooms']

class user:
    def __init__(self,user_obj):
        self.username = user_obj['username']
        self.passhash = user_obj['passhash']
        self.salt = user_obj['salt']
        self.id = user_obj['_id']
        self.token = user_obj['token']
        self.token_date = user_obj['token_date']
        self.student = user_obj['student']
        self.classes = user_obj['classes']

class classroom:
    def __init__(self,user_obj):
        self.class_name = user_obj['class_name']
        self.teacher = user_obj['teacher']
        self.students = user_obj['students']
        self.classcode = user_obj['code']
        self.id = user_obj['_id']

class quiz:
    def __init__(self,user_obj):
        self.class_name = user_obj['class_name']
        self.grades = user_obj['grades']
        self.questions = user_obj['questions']
        self.id = user_obj['_id']


#users -> {username:username,passhash:passwordhash,salt:passwordsalt,_id:user_id,token,exp_date}

def add_user(username,password,student=True):
    check = users.find_one({'username':username})
    if(check != None):
        return False
    else:
        salt = bcrypt.gensalt()
        passhash = bcrypt.hashpw(password.encode('utf-8'),salt)
        users.insert_one({'username':username,'passhash':passhash,'salt':salt,'token':'','token_date':datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),"student":student,"classes":[]})
        return True

#gets the user by their id and returns a user object if found or none if not
def get_user_by_id(id):
    user_found = users.find_one({'_id':ObjectId(id)})
    if(user_found != None):
        return user(user_found)
    else:
        return None

#Gets a users id from their username
def get_id_by_username(username):
    user_found = users.find_one({'username':username})
    if(user_found != None):
        return user_found['_id']
    else:
        return None

#Gets a users username from their id
def get_username_by_id(id):
    user_found = users.find_one({'_id':ObjectId(id)})
    if(user_found != None):
        return user_found['username']
    else:
        return None

def user_delete_by_id(id):
    return users.delete_one({'_id':ObjectId(id)})

#deletes a user by their username 
def user_delete_by_username(username):
    return users.delete_one({'username':username})

def set_user_token(username,token,date=datetime.datetime.now()):
    hash = sha256(token.encode('utf-8')).hexdigest()
    return users.update_many({'username':username},{"$set":{'token':str(hash),"token_date":date}})

def get_user_by_token(token):
    hash = sha256(token.encode('utf-8')).hexdigest()
    u = users.find_one({'token':hash})
    if u != None:
        return user(u)
    else:
        return None

#Gets the user and returns a user object if found or none if not using the users username
def get_user_by_username(username):
    user_found = users.find_one({'username':username})
    if(user_found != None):
        return user(user_found)
    else:
        return None
    
def check_username_exists(username):
    test = users.find_one({'username':username})
    if(test == None):
        return False
    else:
        return True

def check_token(token):
    hash = sha256(token.encode('utf-8')).hexdigest()
    u = users.find_one({'token':hash})
    if u != None:
        if token == 'expired':
            #remove token
            return False
        else:
            return True
    else:
        return False
    

def add_class(class_name,teacher):
    check = classrooms.find_one({'class_name':class_name,'teacher':teacher})
    if(check != None):
        return False
    else:
        #Generating a unique join code
        code = x = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        while(classrooms.find_one({'code':code})!=None):
            code = x = ''.join(random.choices(string.ascii_letters + string.digits, k=8))


        id = classrooms.insert_one({'class_name':class_name,'teacher':teacher,'students':[],'code':code})
        print(id.inserted_id)
        update_user_classes(teacher,str(id.inserted_id))
        return True

def get_class_by_name_and_teacher(class_name,teacher):
    check = classrooms.find_one({'class_name':class_name,'teacher':teacher})
    if(check != None):
        return classroom(check)
    else:
        return None

def get_class_by_id(id):
    check = classrooms.find_one({'_id':ObjectId(id)})
    if(check != None):
        return classroom(check)
    else:
        return None
    
def get_class_by_join_code(code):
    check = classrooms.find_one({'code':code})
    if(check != None):
        return classroom(check)
    else:
        return None

def get_user_classes(username):
    user = get_user_by_username(username)
    classes_found = []
    print(user.classes)
    for id in user.classes:
        found_class = get_class_by_id(id)
        print(found_class)
        if found_class != None:
            classes_found.append(found_class)
    return(classes_found)

def update_user_classes(username,class_id):
    user = get_user_by_username(username)
    if user == None:
        return False
    classes = user.classes
    if class_id not in classes:
        classes.append(class_id)
        users.find_one_and_update({'username':username},{"$set":{"classes":classes}})
        if user.student:
            classroom = get_class_by_id(class_id)
            student_list = classroom.students
            student_list.append(username)
            classrooms.find_one_and_update({'_id':ObjectId(class_id)},{"$set":{"students":student_list}})
        return True
    else:
        return False
