from pymongo import MongoClient
from bson.objectid import ObjectId 
from properties import *
import string, random

uri_local = "mongodb://localhost:27017"
uri_web = db_uri
client = MongoClient(uri_web)
db = client['Waste_Management_System_Bekkah_DB']
Users = db["Users"]
Waste_Donation_Requests = db['Waste_Donation_Requests']
Waste_Donated_Records = db['Waste_Donated_Records']
Location = db['Location']
Notifications = db['Notifications']


class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, details):  
        return self.collection.insert_one(details).inserted_id
        
    def get_active_users_by_role(self, role):
        return self.collection.find({"role": role, "active": "True"})
    
    def get_user_by_role_one(self, role):
        return self.collection.find_one({"role": role})
    
    def get_user_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})
    
    def get_pending_approvals(self):
        return self.collection.find({"status": "pending"})
    
    def get_disabled_users(self):
        return self.collection.find({"status": "Approved","active": False})
    
    def update_user_role(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls}).modified_count>0
    
    def update_user_profile(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$set":dtls}).modified_count>0
    
    def delete_user(self, _id):
        return self.collection.delete_one({"_id":ObjectId(_id)}).deleted_count>0
    
    def get_all_users(self):
        return self.collection.find().sort("uid")
    
    def get_all_users_limited(self):
        return self.collection.find().limit(4)
    
   
    
    
class DonationRequestsdb:
    def __init__(self) -> None:
        self.collection = Waste_Donation_Requests
        
    def create_request(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def update_request(self, request_id, dtls):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":dtls}).modified_count>0

    def delete_request(self, request_id):
        return self.collection.delete_one({"_id":ObjectId(request_id)}).deleted_count>0
    
    def get_specific_request(self, request_id):
        return self.collection.find_one({"_id":ObjectId(request_id)})
    
    def get_requests_by_donor_id(self, donor_id):
        return self.collection.find({"donor_id": donor_id}).sort("datetime_created")
    
    def get_request_by_donor_id_limited(self, donor_id):
        return self.collection.find({"donor_id": donor_id}).sort("datetime_created")
    
    def get_all_request(self):
        return self.collection.find()
    
    def get_all_active_donations(self):
        return self.collection.find({"status": "Pending" or "pending"})
    
    
class Eqptdb:
    def __init__(self) -> None:
        self.collection = Eqpts
    
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0

    def delete_existing_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def get_eqpt_by_name(self, eqpt_name):
        return self.collection.find_one({'$text':{'$search':eqpt_name}})
    
    def get_all_eqpt(self):
        return self.collection.find().sort("name")
    
    def get_all_available_eqpt(self):
        return self.collection.find({"status":"available"}).sort("name")
    
    
class lost_eqptdb:
    def __init__(self) -> None:
        self.collection = lost_eqpts
        
    def new_input(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_eqpt_by_id(self, eqpt_id):
        return self.collection.find_one({"_id":ObjectId(eqpt_id)})
    
    def update_eqpt_dtls(self,eqpt_id, dtls):
        return self.collection.update_one({"_id":ObjectId(eqpt_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_lost_eqpt(self, eqpt_id):
        return self.collection.delete_one({"_id":ObjectId(eqpt_id)}).deleted_count>0
    
    
class Requestdb:
    def __init__(self) -> None:
        self.collection = Requests
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id
    
    def get_all(self):
        return self.collection.find().sort("date_time", -1)
    
    def get_by_request_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1)
    
    def get_by_sender_limited(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1).limit(3)
    
    def get_by_recipient(self, position, _id):
        return self.collection.find({"recipient":{"position":position, "id":ObjectId(_id)}}).sort("date_time", -1)
    
    def get_by_recipient_limited(self, position, user_id):
        return self.collection.find({"recipient":{"position":position, "id":ObjectId(user_id)}}).sort("date_time", -1).limit(3)
    
    def update_request_dtls(self,request_id, dtls):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def delete_request(self, request_id):
        return self.collection.delete_one({"_id":ObjectId(request_id)}).deleted_count>0
    
    def approve_request(self,request_id):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":{"status":"Approved"}}).modified_count>0
    
    def decline_request(self,request_id):
        return self.collection.update_one({"_id":ObjectId(request_id)},{"$set":{"status":"Declined"}}).modified_count>0
 
    
class Reportdb:
    def __init__(self) -> None:
        self.collection = Reports
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id 
    
    def get_all(self):
        return self.collection.find().sort("date_time", -1)
    
    def get_by_report_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1)
    
    def get_by_sender_limited(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1).limit(3)
    
    def get_by_recipient(self, position):
        return self.collection.find({"recipient":position}).sort("date_time", -1)
    
    def get_by_recipient_limited(self, position):
        return self.collection.find({"recipient":position}).sort("date_time", -1).limit(3)
    
    def update_report_dtls(self,report_id, dtls):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def report_feedback(self,report_id, dtls):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":dtls}).modified_count>0
    
    def mark_completed(self,report_id):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":{"status":"Completed"}}).modified_count>0
    
    def mark_incomplete(self,report_id):
        return self.collection.update_one({"_id":ObjectId(report_id)},{"$set":{"status":"Incomplete"}}).modified_count>0
    
    def delete_report(self, report_id):
        return self.collection.delete_one({"_id":ObjectId(report_id)}).deleted_count>0

    
class Projectdb:
    def __init__(self) -> None:
        self.collection = Projects
    
    def insert_new(self, request):
        return self.collection.insert_one(request.__dict__).inserted_id  
    
    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_by_project_id(self, _id):
        return self.collection.find_one({"_id":ObjectId(_id)})
    
    def get_submitted_file(self, id):
        return self.collection.find_one({"submission.id":id})

    def get_by_sender(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1)
    
    def get_by_sender_limited(self, _id, uid):
        return self.collection.find({"sender":{"_id":_id, "uid":uid}}).sort("date_time", -1).limit(4)
    
    def get_by_recipient_dtls(self, category, recipient, name):
        return self.collection.find({"recipient_dtls":{"category":category, "recipient": recipient, "name":name}}).sort("date_time", -1)
    
    def get_by_recipient_dtls_limited(self, category, recipient, name):
        return self.collection.find({"recipient_dtls":{"category":category, "recipient": recipient, "name":name}}).sort("date_time", -1).limit(4)
    
    def update_project_dtls(self, project_id, dtls):
        return self.collection.update_one({"_id":ObjectId(project_id)},{"$set":dtls.__dict__}).modified_count>0
    
    def submit_project(self, project_id, dtls, no_submissions):
        return self.collection.update_one({"_id":ObjectId(project_id)},{"$set":{"submissions":dtls, "no_submissions":no_submissions}}).modified_count>0
    
    def mark_project(self,project_id, project):
        return self.collection.update_one({"_id":ObjectId(project_id)},{"$set":{"submissions":project}}).modified_count>0
    
    def delete_project(self, project_id):
        return self.collection.delete_one({"_id":ObjectId(project_id)}).deleted_count>0
    

class Inventorydb:
    def __init__(self) -> None:
        self.collection = Inventory
    
    def insert_new(self, dtls):
        return self.collection.insert_one(dtls.__dict__).inserted_id
    
    def get_all(self):
        return self.collection.find().sort("date_inserted")
    
class Attendancedb:
    def __init__(self) -> None:
        self.collection = Attendance
    
    def sign_in(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def sign_out(self, attendance_id, time_out, status):
        return self.collection.update_one({"_id":ObjectId(attendance_id)},{"$set":{"time_out": time_out, "status": status}}).modified_count>0
    
    def get_attendance(self, user_id):
        return self.collection.find({"user_id": user_id}).sort("date_time", -1).limit(3)
     

class Attendancedb_v2:
    def __init__(self) -> None:
        self.collection = Attendance_v2
    
    def sign_in(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def sign_out(self, attendance_id, time_out, status):
        return self.collection.update_one({"_id":ObjectId(attendance_id)},{"$set":{"time_out": time_out, "status": status}}).modified_count>0
    
    def get_attendance(self, user_id):
        return self.collection.find({"user_id": user_id}).sort("date_time", -1).limit(3)
     
    def get_user_attendance_by_date(self, user_uid, date):
        return self.collection.find({"user_uid": user_uid, "date":date})
    
    def get_marked_in_users(self, date):
        return self.collection.find({"date": date, "status": "in"}).sort("date_time", -1)
    
    
class generate:   
    def password():
        password_length = int(12)
        characters = string.ascii_letters + string.digits
        password = ""   
        for index in range(password_length):
            password = password + random.choice(characters)
            
        return password

    def user_id(firstname):
        max = int(3)
        digits = string.digits
        #while 1:
            
        _id = firstname + "SSRL"
        
        for index in range(max):
            _id = _id + random.choice(digits)
            
            # if Users.find_one({"pwd":_id}) == "None": 
            #     break
            
        return _id 
    
    def file_id():
        max = int(16)
        digits = string.digits
        file_id = ""
        
        for index in range(max):
            file_id = file_id + random.choice(digits)
            
            # if Users.find_one({"pwd":_id}) == "None": 
            #     break
            
        return file_id 
    
    def OTP():
        length = int(6)
        characters = string.digits
        otp = ""     
        for index in range(length):
            otp = otp + random.choice(characters)
            
        return otp
    
class User:
    def __init__(self, firstname, surname, fullname, hashed_pwd, uid, stack, niche, role, phone_num, email, mentor_id, avatar, task_id, bio, location, bday, datetime_created) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self. hashed_pwd = hashed_pwd
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.mentor_id = mentor_id
        self.avatar = avatar
        self.task_id = task_id   
        self.datetime_created = datetime_created
        self.bio = bio
        self.location = location
        self.bday = bday

class Eqpt:
    def __init__(self, name, quantity, description, date_of_arrival, type, status, datetime_inputed, date_inserted) -> None:
        self.name = name
        self.quantity = quantity
        self.description = description
        self.date_of_arrival = date_of_arrival
        self.type = type
        self.status = status
        self.datetime_inputed = datetime_inputed
        self.date_inserted = date_inserted
        
class existEqpt:
    def __init__(self, quantity, datetime_inputed, status) -> None:
        self.quantity = quantity
        self.datetime_inputed = datetime_inputed
        self.status = status

class lostEqpt:
    def __init__(self, eqpt_id, name, type, quantity, personnel_id, status, date_reported, date_edited) -> None:
        self.eqpt_id = eqpt_id
        self.name = name
        self.type = type
        self.quantity = quantity
        self.personnel_id = personnel_id
        self.status = status
        self.date_reported = date_reported
        self.date_edited = date_edited

class updateUser:
    def __init__(self, filename, phone_num, bio, location, bday) -> None:
        self.avatar = filename
        self.phone_num = phone_num
        self.bio = bio
        self.location = location
        self.bday = bday
        
class updateAdmin:
    def __init__(self, firstname, surname, fullname, uid, stack, niche, role, filename, phone_num, email, bio, location, bday) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        self.phone_num = phone_num
        self.email = email
        self.avatar = filename 
        self.bio = bio
        self.location = location
        self.bday = bday

class AdminUpdateUser:
    def __init__(self, firstname, surname, fullname, uid, stack, niche, role) -> None:
        self.firstname = firstname
        self.surname = surname
        self.fullname = fullname
        self.uid = uid
        self.stack = stack
        self.niche = niche
        self.role = role
        
class Request:
    def __init__(self, title, type, eqpt, quantity, date_from, date_to, purpose, sender, recipient_dtls, status, date_submitted, date_time) -> None:
        self.title = title
        self.type = type
        self.eqpt = eqpt
        self.quantity = quantity
        self.date_from = date_from
        self.date_to = date_to
        self.purpose = purpose
        self.sender = sender
        self.recipient = recipient_dtls
        self.status = status
        self.date_submitted = date_submitted
        self.date_time = date_time
        
class Project:
    def __init__(self, topic, focus, objectives, recipient_dtls, sender, date_created, deadline, date_time) -> None:
        self.topic = topic
        self.focus = focus
        self.objectives = objectives
        self.recipient_dtls = recipient_dtls
        self.sender = sender
        self.date_created = date_created
        self.deadline = deadline
        self.date_time = date_time
        
class Report:
    def __init__(self, title, report_no, content, recipient, sender, date_submitted, status, date_time) -> None:
        self.title = title
        self.report_no = report_no
        self.content = content
        self.recipient = recipient
        self.sender = sender
        self.date_submitted = date_submitted
        self.status = status
        self.date_time = date_time
        
class AllowedExtension:    
    def images(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def files(filename):
        ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docs','docx'} 
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Available:
    def __init__(self, _quantity, _status) -> None:
        self.status = _status
        self.quantity = _quantity
    
class updateEmail:
    def __init__(self, new_email) -> None:
        self.email = new_email
        
class updatePwd:
    def __init__(self, hashed_pwd) -> None:
        self.hashed_pwd = hashed_pwd
        
def formatAttendance(dtls):
    user_dtls = []
    for dtl in dtls:
        user_dtl = {}
        user_dtl["user_uid"] = dtl["user_uid"]
        user_dtl["date"] = dtl["date"]
        user_dtl["time_in"] = dtl["time_in"]
        user_dtls.append(user_dtl)
        
    return user_dtls

def sortFunc(e):
  return e["date_time"]



