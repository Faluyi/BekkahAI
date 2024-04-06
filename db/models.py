from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
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
Delivery_Confirmation_Requests = db["Delivery_Confirmation_Requests"]
Waste_point_rates = db["Waste_point_rates"]

Users.create_index([('email', ASCENDING)], unique=True)
Location.create_index({"location": "2dsphere" })

class Userdb:
    def __init__(self) -> None:
        self.collection =  Users

    def create_user(self, details):  
        return self.collection.insert_one(details).inserted_id
        
    def get_active_users_by_role(self, role):
        return self.collection.find({"role": role, "active": True}).sort([('_id', -1)])
    
    def get_user_by_role_one(self, role):
        return self.collection.find_one({"role": role})
    
    def get_master_by_location(self, location):
        return self.collection.find_one({"role": "waste-master", "location": location, "active": True})
    
    def get_aggregators_by_location(self, location):
        return self.collection.find({"role": "waste-aggregator", "location": location, "active": True})
    
    def get_user_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id), "active": True})
    
    def get_pending_approvals(self):
        return self.collection.find({"status": "pending"}).sort([('_id', -1)])
    
    def get_disabled_users(self):
        return self.collection.find({"status": "Approved","active": False}).sort([('_id', -1)])
    
    def update_user_role(self, user_id, dtls):
        return self.collection.update_one({"uid":user_id},{"$set":dtls}).modified_count>0
    
    def update_user_profile(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$set":dtls}).modified_count>0
    
    def update_user_notifications(self, _id, dtls):
        return self.collection.update_one({"_id": ObjectId(_id)},{"$push": {"notifications": {"$each": [dtls], "$position": 0}}}).modified_count>0
    
    def mark_notification_as_read(self, user_id, donation_id):
        return self.collection.update_one({"_id": ObjectId(user_id), 'notifications.donation_id': donation_id},{'$set': {'notifications.$.read': True}}).modified_count>0
    
    def delete_user(self, _id):
        return self.collection.delete_one({"_id":ObjectId(_id)}).deleted_count>0
    
    def get_all_users_limited(self):
        return self.collection.find().limit(4)
    
    def increment_pending_waste_points(self, _id, points):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'pending_waste_points': points}},  upsert=True )
    
    def increment_valid_waste_points(self, _id, points):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'valid_waste_points': points}},  upsert=True )
    
    def decrement_pending_waste_points(self, _id, points):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'pending_waste_points': -points}})
    
    def decrement_valid_waste_points(self, _id, points):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'valid_waste_points': -points}})
    
    def insert_active_donations_aggregator_id(self, donor_id, aggregator_id):
        return self.collection.update_one({"_id": ObjectId(donor_id)},{"$push":{"active_donations_aggregator_id": aggregator_id}}).modified_count>0

    def remove_active_donations_aggregator_id(self, donor_id, aggregator_id):
        return self.collection.update_one({"_id": ObjectId(donor_id)},{"$pull": {"active_donations_aggregator_id": aggregator_id}}).modified_count > 0
    
    def increment_total_number_of_donations(self, _id):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'total_donations': 1}},  upsert=True ) 
    
    def increment_total_number_of_picked_donations(self, _id):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'total_donations_picked': 1}},  upsert=True ) 
    
    def increment_total_waste_weight_donated(self, _id, waste_weight):
        return self.collection.update_one({'_id': ObjectId(_id)}, {'$inc': {'total_waste_weight_donated': waste_weight}},  upsert=True )  
    
    def update_weightiest_waste_donated(self, user_id, weight):
        return self.collection.update_one({"_id": ObjectId(user_id), "weightiest_waste_donated": weight})
    
    
    
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
        return self.collection.find({"donor_id": donor_id}).sort([('_id', -1)])
    
    def get_requests_by_aggregator_id(self, aggregator_id):
        return self.collection.find({"aggregator.id": aggregator_id}).sort([('_id', -1)])
    
    def get_request_by_donor_id_limited(self, donor_id):
        return self.collection.find({"donor_id": donor_id}).sort([('_id', -1)])
    
    def get_all_active_donations(self):
        return self.collection.find({"status": "Active"}).sort([('_id', -1)])
    
    def get_all_completed_donations(self):
        return self.collection.find({"status": "Completed"}).sort([('_id', -1)])
    
    def get_all_completed_donations_waste_master(self, master_location):
        return self.collection.find({"status": "Completed", "drop_off_location": master_location}).sort([('_id', -1)])
    
    def get_all_completed_donations_waste_aggregator(self, aggregator_id):
        return self.collection.find({"status": "Completed", "aggregator": {"id": aggregator_id}}).sort([('_id', -1)])
    
    def get_all_active_donations_by_location(self, location):
        return self.collection.find({"status": "Pending", "drop_off_location": location}).sort([('_id', -1)])

    def get_all_active_donations_by_aggregator_id(self, aggregator_id):
        status_values = ["Active", "picked"]
        return self.collection.find({"status": {"$in": status_values}, "aggregator.id": aggregator_id}).sort([('_id', -1)])
    
    def get_all_pending_requests_by_aggregrator(self):
        return self.collection.find({"status":"Pending"}).sort([('_id', -1)])
    
    
class Locationsdb:
    def __init__(self) -> None:
        self.collection = Location
        
    def new_input(self, dtls):
        return self.collection.insert_one(dtls).inserted_id

    def get_all(self):
        return self.collection.find().sort("date_time")
    
    def get_location_by_id(self, location_id):
        return self.collection.find_one({"_id":ObjectId(location_id)})
    
    def get_location_by_user_id(self, user_id):
        return self.collection.find_one({"user_id":user_id})
    
    def update_location_data(self,user_id, new_coordinates):
        return self.collection.update_one({"user_id": user_id}, {"$set": {"location": {"type": "Point", "coordinates": new_coordinates}}}).modified_count>0
    
    def get_users_within_radius(self, pickup_location, radius) -> list:
        return self.collection.find({ "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [pickup_location["longitude"], pickup_location["latitude"]]
                },
                "$maxDistance": radius * 1000
            }
        }})
    
    
class ConfirmationRequestsdb:
    def __init__(self) -> None:
        self.collection = Delivery_Confirmation_Requests
        
    def create_request(self, dtls):
        return self.collection.insert_one(dtls).inserted_id
    
    def get_requests(self, user_id):
        return self.collection.find({"master_id": user_id, "confirmed": False}).sort([('_id', -1)])
    
    def get_confirmed_deliveries(self, user_id):
        return self.collection.find({"master_id": user_id, "confirmed": True}).sort([('_id', -1)])
        
    def confirm_delivery(self, donation_id, dtls):
        return self.collection.update_one({"donation_id":donation_id},{"$set":dtls}).modified_count>0

    def delete_request(self, request_id):
        return self.collection.delete_one({"_id":ObjectId(request_id)}).deleted_count>0
    
    def get_specific_request(self, request_id):
        return self.collection.find_one({"_id":ObjectId(request_id)})


class WastePointRatesdb:
    def __init__(self) -> None:
        self.collection = Waste_point_rates
    
    def set_rate(self, role, rate):
        return self.collection.insert_one({"role": role, "rate": rate}).inserted_id
    
    def update_rate(self, role, rate):
        return self.collection.update_one({"role": role},{"$set":{"rate": rate}}).modified_count>0
    
    def get_rate(self, role):
        return self.collection.find_one({"role": role})
    
  
class Notifications:
    
    def get_pickup_requests(user_notifications):
    
        requests = []
        for notification in user_notifications:
            if notification["status"] == "Pending":
                requests.append(notification)

        return requests

    def get_active_donations(user_notifications):
        
        requests = []
        for notification in user_notifications:
            if notification["status"] == "Active":
                requests.append(notification)

        return requests
    
    def get_active_donations_aggregators(user_notifications):
        
        requests = []
        for notification in user_notifications:
            if notification["status"] == "Active":
                requests.append(notification)

        return requests

    def get_completed_requests(user_notifications):
        
        requests = []
        for notification in user_notifications:
            if notification["status"] == "Completed":
                requests.append(notification)

        return requests
        

    
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
    

