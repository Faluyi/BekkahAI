from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from db.models import *
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from datetime import datetime
from flask_cors import CORS
from auth import authenticate_user, token_required
import jwt
from properties import *
from pymongo.errors import DuplicateKeyError



app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="https://wastemanagementapp.waste4meal.com")


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'faluyiisaiah@gmail.com'
app.config['MAIL_PASSWORD'] = mail_pswd
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True   
mail = Mail(app)


bcrypt = Bcrypt(app)
Users_db = Userdb()
Donations_requests_db = DonationRequestsdb()
Notifications_db = Notifications()
Locations_db = Locationsdb()

SECRET_KEY = "bekkah"
app.config['SECRET_KEY'] = SECRET_KEY




@app.post('/api/register')
def register():
    body = request.get_json()
    app.logger.info(body)
    
    for value in body.values():
        if value == "":
            return {
                "status": "failed",
                "message": "Field missing!",
            }, 400
    
   
    if body["role"] == "donor":
        
        if body["password"] != body["confirmPassword"]:
            return {
                "status": "failed",
                "message": "Passwords do not match!"
            }, 400
            
        registration_details = {
        "first_name" : body["first_name"],
        "last_name" : body["last_name"],
        "email" : body["email"],
       "role" : body["role"],
       "password" : generate_password_hash(body["password"]),
       "phone_number": body["phone_number"],
       "address" : body["address"],
       "date_approved": datetime.now(),
       "active": True
    }
    
    elif body["role"] == "waste-aggregator":
    
            
            registration_details = {
            "first_name" : body["first_name"],
            "last_name" : body["last_name"],
            "email" : body["email"],
            "role" : body["role"],
            "status": "pending",
            "phone_number": body["phone_number"],
            "address" : body["address"],
            "capacity" : body["capacity"],
            "date-registered": datetime.now(),
            "active": False
            }
            
        
    else:
        
        registration_details = {
        "first_name" : body["first_name"],
        "last_name" : body["last_name"],
        "email" : body["email"],
        "role" : body["role"],
        "status": "pending",
        "phone_number": body["phone_number"],
        "address" : body["address"],
        "capacity" : body["capacity"],
        "date-registered": datetime.now(),
        "active": False
    }
    
    try:
        inserted  = Users_db.create_user(registration_details)
        
        if inserted:
            return {
                "status": "success",
                "message": "User registration successful"
            }, 200
            
    except DuplicateKeyError:
        return {
            "status": "failed",
            "message": "Email address already in use"
        }, 400
        
    except :
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
@app.post("/api/sign_in")
def sign_in():
    
    body = request.get_json()
    
    for value in body.values():
        if value == '':
            return {
                "status": "failed",
                "message": "Field missing !",
            }, 400
    
    email = body["email"]
    password = body["password"] 
    
    user_profile = authenticate_user(email, password)
    
    if user_profile == "not found":
        return {
            "status": "failed",
            "message": "Invalid email address !"
        }, 404
        
    if user_profile:
        try:
            token = jwt.encode({
                "user_id": str(user_profile["_id"]),
                "role": user_profile["role"]
            }, app.config["SECRET_KEY"], algorithm="HS256")
            app.logger.info(token)
            return jsonify({
                "status": "success",
                "message": "Authentication successful",
                "response": {
                    "token": token,
                    "role": user_profile["role"],
                    "user_id": str(user_profile["_id"])
                }
            }), 200
        
        except Exception as e:
            app.logger.exception(e)
            return {
                "status": "failed",
                "message": "Authentication failed",
            }, 500
    
    else:
        return {
            "status": "failed",
            "message": "Invalid password!"
        }, 401


@app.get('/api/user')
@token_required
def current_user_profile(current_user):
    user_id = current_user["_id"]
    
    try:
        user = Users_db.get_user_by_id(user_id)
        # notifications = list(Notifications_db.get_notifications_by_location(user["location"]))
        # for notification in notifications:
        #     notification["_id"] = str(notification["_id"])
        # app.logger.info(user)
        # app.logger.info(notifications)
        
        user["_id"] = str(user["_id"])
        del user["password"]
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "response": user,
            # "notifications": notifications
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500
        
@app.patch('/api/user/<user_id>/update')
@token_required
def update_user_profile(current_user, user_id):
    body = request.get_json()
    app.logger.info(body)
    app.logger.info(user_id)
    
    try:
        Users_db.update_user_profile(user_id, body)
        user = Users_db.get_user_by_id(user_id)
        user["_id"] = str(user["_id"])
        del user["password"]  
        return {
            "status": "success",
            "message": "User profile updated successfully",
            "response": user
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500

@app.patch('/api/user/<user_id>/change_password')
@token_required
def update_user_password(current_user, user_id):
    body = request.get_json()
    app.logger.info(body)
    app.logger.info(user_id)
    
    for value in body.values():
        if value == '':
            return {
                "status": "failed",
                "message": "Field missing!",
            }, 400
    
    try:
        user = Users_db.get_user_by_id(user_id)
        app.logger.info(user["password"])
        if not check_password_hash(user["password"], body['old_password']) :
            return {
            "status": "failed",
            "message": "Unauthorized request"
        }, 401
        
        if body["new_password_1"] == body["new_password_2"]:
            new_password = generate_password_hash(body["new_password_1"])
            Users_db.update_user_profile(user_id, {"password": new_password})
             
            return {
                "status": "success",
                "message": "Password changed successfully",
            }, 200
        
        else:
            return {
            "status": "failed",
            "message": "Unmatching passwords"
        }, 404
        
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500
        
        
@app.patch('/api/user/<user_id>/change_email')
@token_required
def update_user_email(current_user, user_id):
    body = request.get_json()
    app.logger.info(body)
    app.logger.info(user_id)
    
    
    try:
        user = Users_db.get_user_by_id(user_id)
        
        if check_password_hash(user["password"], body['old_password']) :

            return {
            "status": "failed",
            "message": "Unauthorized request"
        }, 401
        
        new_email = body["new_email"]
        Users_db.update_user_profile(user_id, {"email": new_email})
            
        return {
            "status": "success",
            "message": "Email changed successfully",
        }, 200
        
       
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500
        
@app.get('/api/user/<user_id>')
@token_required
def user_profile(current_user, user_id):
    
    try:
        user = Users_db.get_user_by_id(user_id)
        
        user["_id"] = str(user["_id"])
        del user["password"]
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "response": user
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal server error"
        }, 500
    

@app.post('/api/donate')
@token_required
def donate(current_user):
    body = request.get_json()
   
    app.logger.info(body)
    for value in body.values():
            if value == '':
                return {
                    "status": "failed",
                    "message": "A required field is missing!",
                }, 400


   
    
    try:
        
        
        pickup_location = {
            "longitude": body["long"],
            "latitude": body["lat"]
        }
        
        radius = 10
        aggregators_within_radius = list(Locations_db.get_users_within_radius(pickup_location, radius))
        app.logger.info(aggregators_within_radius)
        aggregators = []
        for aggregator in aggregators_within_radius:
            aggregator_id = str(aggregator["user_id"])
            aggregators.append(aggregator_id)
            
        request_details = {
            'donor_id': current_user["_id"],
            'category': body["category"],
            'weight': body["weight"],
            'pickup_location':{
                "address": body["pickup_location"],
                "latitude": body["lat"],
                "longitude": body["long"]
            },
            'scheduled_pickup_time': body["checked_radio_button"],
            'status': 'Pending',
            'aggregators': aggregators,
            'datetime_created': datetime.now()
        }
        
        request_id = Donations_requests_db.create_request(request_details)
        
        notification_details = {
       "title": "Pick-up request",
       "donation_id": str(request_id),
       "pickup_address": body["pickup_location"],
       "waste_weight": body["weight"],
       "waste_category": body["category"],
       "date_time": datetime.now(),
       "status": "Pending",
       "read": False
   }
        for id in aggregators:
            
            Users_db.update_user_notifications(id, notification_details)
        
            
        return {
            "status": "success",
            "message": "Donation request created",
            "response": {
                'request_id': str(request_id)
            }
        }, 200
        
       
       
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "failed",
            "message": "Failed to create donation request, please try again!"
        }, 500
        
        
    
@app.get('/api/donations')
@token_required
def get_all_donations(current_user):
    app.logger.info(current_user)
    
    try:
        request_details = list(Donations_requests_db.get_requests_by_donor_id(current_user["_id"]))
        app.logger.info(request_details)
        for request in request_details:
            request["_id"] = str(request["_id"])
            request["donor_id"] = str(request["donor_id"])
        
        return {
            "status": "success",
            "message": "Donation requests found",
            "response": {
                "request_details": request_details,
                "length": len(request_details)
                }
        }, 200
    
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500      
       
@app.get('/api/donation/<donation_id>')
@token_required
def get_donation(current_user, donation_id):
    app.logger.info(donation_id)
    
    try:
        request_details = Donations_requests_db.get_specific_request(donation_id)
        app.logger.info(current_user)
        
        app.logger.info(request_details)
        if request_details:
            request_details["_id"] = str(request_details["_id"])
            request_details["donor_id"] = str(request_details["donor_id"])
            request_details["user_role"] = current_user["role"]
            return {
                "status": "success",
                "message": "Donation request found",
                "response": request_details
            }, 200
        else:
            return {
                "status": "failed",
                "message": "Donation request not found"
            }, 404
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
       
@app.patch('/api/donation/<donation_id>/interested')
@token_required
def interested(current_user, donation_id):
    app.logger.info(donation_id)
    
    try:
        request_details = Donations_requests_db.get_specific_request(donation_id)
        app.logger.info(request_details)
        
        if request_details["status"] == "Pending": 
            aggregator_details = {
                "aggregator": {
                    "id": str(current_user["_id"]),
                    "name": current_user["first_name"] + " " + current_user["last_name"],
                    "phone_number": current_user["phone_number"]
                },
                "status": "Active"
            }
        
            Donations_requests_db.update_request(donation_id, aggregator_details)
        
        
            return {
            "status": "success",
            "message": "Donation request accpeted successfully",
        }, 200
        
        else:
            return {
                "status": "failed",
                "message": "Donation request no longer available!",
            }, 404
            
  
       
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
  
    
@app.patch('/api/donation/<donation_id>/picked')    
@token_required
def pick_donation(current_user, donation_id):
    
    body = request.get_json()
    app.logger.info(body)
    
    if "" in body.values():
        return {
            "status": "failed",
            "message": "A required field is missing!",
        }, 400
    
    try:
        donation_dtls = Donations_requests_db.get_specific_request(donation_id)
        earned_points_pending = ((float(body["weight"])) * 1000) / 100
        notification_details = {
            "title": "Waste picked",
            "donation_id": str(donation_dtls["donor_id"]),
            "earned_waste_points": earned_points_pending,
            "date_time": datetime.now(),
            "status": "picked",
            "read": False
        }
        Donations_requests_db.update_request(donation_id, {"status": "picked", "weight": body["weight"], "pickup_time": datetime.now(), "earned_points_donor": earned_points_pending})
        Users_db.increment_pending_waste_points(str(donation_dtls["donor_id"]), earned_points_pending)
        Users_db.update_user_notifications(str(donation_dtls["donor_id"]), notification_details)
        Users_db.insert_active_donations_aggregator_id(str(donation_dtls["donor_id"]),str(current_user["_id"]))
        Users_db.increment_total_number_of_donations(str(donation_dtls["donor_id"]))
        Users_db.increment_total_waste_weight_donated(str(donation_dtls["donor_id"]), float(body["weight"]))
        
        
        
        return {
            "status": "success",
            "message": "Waste picked!",
        }, 200
        
        
    except Exception as e:
        app.logger.info(e)
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500

@app.patch('/api/donation/<donation_id>/completed')    
@token_required
def complete_donation(current_user, donation_id):
    
    body = request.get_json()
    app.logger.info(body)
    
    try:
        donation_dtls = Donations_requests_db.get_specific_request(donation_id)
        earned_points_pending = (float(body["weight"]) * 1000) / 100
        notification_details = {
            "title": "Waste donation delivered",
            "donation_id": str(donation_dtls["donor_id"]),
            "earned_waste_points": earned_points_pending,
            "date_time": datetime.now(),
            "status": "Completed",
            "read": False
        }
        
        Donations_requests_db.update_request(donation_id, {"status": "Completed", "completion_time": datetime.now()})
        Users_db.decrement_pending_waste_points(str(donation_dtls["donor_id"]), earned_points_pending)
        Users_db.increment_valid_waste_points(str(donation_dtls["donor_id"]), earned_points_pending)
        Users_db.update_user_notifications(str(donation_dtls["donor_id"]), notification_details)
        Users_db.remove_active_donations_aggregator_id(str(donation_dtls["donor_id"]), donation_dtls["aggregator"]["id"])
        Users_db.increment_total_number_of_picked_donations(str(donation_dtls["aggregator"]["id"]))
        return {
            "status": "success",
            "message": "Waste donation successfully delivered!",
        }, 200
        
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500

    
        
@app.get('/api/dashboard/admin')
@token_required
def admin_dashboard(current_user):
    
    try:
        pending_approvals = list(Users_db.get_pending_approvals())
        active_donations = list(Donations_requests_db.get_all_active_donations())
        disabled_users = list(Users_db.get_disabled_users())
        active_donors = list(Users_db.get_active_users_by_role("donor"))
        active_aggregators = list(Users_db.get_active_users_by_role("waste-aggregator"))
        active_waste_masters = list(Users_db.get_active_users_by_role("waste-master"))
        
        app.logger.info(pending_approvals)
        app.logger.info(active_donations)
        app.logger.info(disabled_users)
        app.logger.info(active_donors)
        app.logger.info(active_aggregators)
        app.logger.info(active_waste_masters)
        
        return {
            "status": "success",
            "message": "Reports fetched successfully",
            "response": {
                "pending_approvals": len(pending_approvals),
                "active_donations": len(active_donations),
                "disabled_users": len(disabled_users),
                "active_donors": len(active_donors),
                "active_aggregators": len(active_aggregators),
                "active_waste_masters": len(active_waste_masters)
            }
        }, 200

    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.get('/api/dashboard/master')
@token_required
def master_dashboard(current_user):
    
    try:
        active_donations = list(Donations_requests_db.get_all_active_donations_by_location(current_user["location"]))
        active_aggregators = list(Users_db.get_aggregators_by_location(current_user["location"]))
        completed_donations = list(Donations_requests_db.get_all_completed_donations_waste_master(current_user["location"]))

        app.logger.info(active_donations)
        app.logger.info(active_aggregators)
        
        return {
            "status": "success",
            "message": "Reports fetched successfully",
            "response": {
                "active_donations": len(active_donations),
                "active_aggregators": len(active_aggregators),
                "active_aggregators": len(completed_donations),
            }
        }, 200

    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.get('/api/dashboard/aggregator')
@token_required
def aggregator_dashboard(current_user):
    app.logger.info(current_user["notifications"])
          
    try:
        pickup_requests = []
        completed_donations = list(Donations_requests_db.get_all_completed_donations_waste_aggregator(str(current_user["_id"])))
        
        for request in list(Donations_requests_db.get_all_pending_requests_by_aggregrator()):
            if str(current_user["_id"]) in request["aggregators"]:
                pickup_requests.append(request)
                
        
        active_donations = list(Donations_requests_db.get_all_active_donations_by_aggregator_id(str(current_user["_id"])))
        
        app.logger.info(pickup_requests)
        app.logger.info(active_donations)
        app.logger.info(completed_donations)
        
        return {
            "status": "success",
            "message": "Reports fetched successfully",
            "response": {
                "pickup_requests": len(pickup_requests),
                "active_donations": len(active_donations),
                "completed_donations": len(completed_donations)
            }
        }, 200

    except Exception as e:
        app.logger.info(e)
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.get('/api/pending-approvals')
@token_required
def get_pending_approvals(current_user):
    
    try:
        pending_approvals = list(Users_db.get_pending_approvals())
        app.logger.info(pending_approvals)
        for pending_approval in pending_approvals:
            pending_approval['_id'] = str(pending_approval['_id'])
        return {
            "status": "success",
            "message": "Pending approvals fetched successfully",
            "response": pending_approvals
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
@app.get('/api/donations/pending')
@token_required
def get_pending_donations(current_user):
    
    try:
        pickup_requests = []
        for request in list(Donations_requests_db.get_all_pending_requests_by_aggregrator()):
            if str(current_user["_id"]) in request["aggregators"]:
                request["_id"] = str(request["_id"])
                pickup_requests.append(request)
                request["donor_id"] = str(request['donor_id'])
        app.logger.info(pickup_requests)
        return {
            "status": "success",
            "message": "Active donations fetched successfully",
            "response": pickup_requests
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
@app.get('/api/donations/active')
@token_required
def get_active_donations(current_user):
    
    try:
        if current_user["role"] == "Admin":
            active_donations = list(Donations_requests_db.get_all_active_donations())
            
            for donation in active_donations:
                donation["_id"] = str(donation['_id'])
                donation["donor_id"] = str(donation['donor_id'])
            app.logger.info(active_donations)
            return {
                "status": "success",
                "message": "Active donations fetched successfully",
                "response": active_donations
            }, 200
        
        else:
            active_donations = list(Donations_requests_db.get_all_active_donations_by_aggregator_id(str(current_user["_id"])))
            for donation in active_donations:
                donation["_id"] = str(donation['_id'])
                donation["donor_id"] = str(donation['donor_id'])
            app.logger.info(active_donations)
            return {
                "status": "success",
                "message": "Active donations fetched successfully",
                "response": active_donations
            }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
@app.get('/api/donations/completed')
@token_required
def get_completed_donations(current_user):
    
    try:
        if current_user["role"] == "Admin":
            completed_donations = list(Donations_requests_db.get_all_completed_donations())
            
            for donation in completed_donations:
                donation["_id"] = str(donation['_id'])
                donation["donor_id"] = str(donation['donor_id'])
            app.logger.info(completed_donations)
            return {
                "status": "success",
                "message": "Completed donations fetched successfully",
                "response": completed_donations
            }, 200
        
        elif current_user["role"] == "waste-master":
            completed_donations = list(Donations_requests_db.get_all_completed_donations_waste_master(current_user["location"]))
            for donation in completed_donations:
                donation["_id"] = str(donation['_id'])
                donation["donor_id"] = str(donation['donor_id'])
            app.logger.info(completed_donations)
            return {
                "status": "success",
                "message": "Completed donations fetched successfully",
                "response": completed_donations
            }, 200
            
        elif current_user["role"] == "waste-aggregator":
            completed_donations = list(Donations_requests_db.get_all_completed_donations_waste_aggregator(str(current_user["_id"])))
            for donation in completed_donations:
                donation["_id"] = str(donation['_id'])
                donation["donor_id"] = str(donation['donor_id'])
            app.logger.info(completed_donations)
            return {
                "status": "success",
                "message": "Completed donations fetched successfully",
                "response": completed_donations
            }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500


@app.get('/api/users/disabled')
@token_required
def get_disabled_users(current_user):
           
    try:
        disabled_users = list(Users_db.get_disabled_users())
        
        for user in disabled_users:
            user["_id"] = str(user["_id"])
            del user["password"]
        
        app.logger.info(disabled_users)
        return {
            "status": "success",
            "message": "List of disables users fetched successfully",
            "response": disabled_users
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.get('/api/users/donors')
@token_required
def get_active_donors(current_user):
           
    try:
        active_donors = list(Users_db.get_active_users_by_role("donor"))
        
        for donor in active_donors:
            donor["_id"] = str(donor["_id"])
            del donor["password"]
            
        app.logger.info(active_donors)
        return {
            "status": "success",
            "message": "List of active donors fetched successfully",
            "response": active_donors
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
        
@app.get('/api/users/aggregators')
@token_required
def get_active_waste_aggregators(current_user):
           
    try:
        active_aggregators = list(Users_db.get_active_users_by_role("waste-aggregator"))
        for aggregator in active_aggregators:
            aggregator["_id"] = str(aggregator["_id"])
            del aggregator["password"]
        
        app.logger.info(active_aggregators)
        return {
            "status": "success",
            "message": "List of active aggregators fetched successfully",
            "response": active_aggregators
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
   
        
@app.get('/api/users/waste_masters')
@token_required
def get_active_waste_masters(current_user):
           
    try:
        active_waste_masters = list(Users_db.get_active_users_by_role("waste-master"))
        for waste_master in active_waste_masters:
            waste_master["_id"] = str(waste_master["_id"])
            del waste_master["password"]
        
        app.logger.info(active_waste_masters)
        return {
            "status": "success",
            "message": "List of active waste masters fetched successfully",
            "response": active_waste_masters
        }, 200
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500

@app.patch('/api/user/<user_id>/approve')
@token_required
def approve(current_user, user_id):
    try:
        password = generate.password()
        password_hash = generate_password_hash(password)
        
        
        user = Users_db.get_user_by_id(user_id)
        approved = Users_db.update_user_profile(user_id, {"status": "Approved", "active": True, "password": password_hash})
        app.logger.info(password)
        app.logger.info(approved)
        app.logger.info(user)
        
        if approved:
            try: 
                msg = Message('Account Approval', sender = 'faluyiisaiah@gmail.com', recipients=[user["email"]])
                msg.body = f'Your account has been approved. Your login credentials are:\nEmail: {user["email"]}\nPassword: {password}\nPlease sign in and update your profile.'
                mail.send(msg)
            
                return {
                    "status": "success",
                    "message": "User approved successfully",
                    "response": {
                        "status": "Approved" 
                    }
                }, 200
            
            except:
                app.logger.info("email not sent")
                return {
            "status": "failed",
            "message": "Email not sent"
        }, 500
        
        else:
            return {
                "status": "failed",
                "message": "Bad request"
            }, 400
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.patch('/api/user/<user_id>/reject')
@token_required
def reject(current_user, user_id):
    try:
        rejected = Users_db.update_user_profile(user_id, {"status": "Rejected"})
        
        if rejected:
            return {
                "status": "success",
                "message": "User Rejected successfully",
                "response": {
                    "status": "Rejected" 
                }
            }, 200
        else:
            return {
                "status": "failed",
                "message": "Bad request"
            }, 400
        
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        

        
@app.patch('/api/user/<user_id>/disable')
@token_required
def disable_user(current_user, user_id):
    
    try:
        disabled = Users_db.update_user_profile(user_id, {"active": False})

        if disabled:
            return {
                "status": "success",
                "message": "User disabled successfully",
                "response": {
                    "status": "Disabled" 
                }
            }, 200
        else:
            return {
                "status": "failed",
                "message": "Bad request"
            }, 400
            
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
        
@app.patch('/api/user/<user_id>/activate')
@token_required
def activate_user(current_user, user_id):
    
    try:
        activated = Users_db.update_user_profile(user_id, {"active": True})

        if activated:
            return {
                "status": "success",
                "message": "User activated successfully",
                "response": {
                    "status": "Activated" 
                }
            }, 200
        else:
            return {
                "status": "failed",
                "message": "Bad request"
            }, 400
            
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500
    
    
    
@app.delete('/api/donation/<donation_id>/delete')
@token_required
def delete_donation(current_user, donation_id):
    
    try:
        deleted = Donations_requests_db.delete_request(donation_id)

        if deleted:
            return {
                "status": "success",
                "message": "Donation request deleted successfully",
            }, 200
        else:
            return {
                "status": "failed",
                "message": "Bad request"
            }, 400
            
    except:
        return {
            "status": "failed",
            "message": "Internal Server Error"
        }, 500

@socketio.on('connect')
def handle_connect():
    app.logger.info('Client connected')
    
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    
    
@socketio.on('get_location')
def handle_get_location(data):
    app.logger.info(data)
    location_data = {
        "user_id": data["user_id"],
        "role": data["role"],
        "location": {"type": "Point", "coordinates": [data['longitude'], data['latitude']]}
    }
    try:
        Locations_db.update_location_data(data["user_id"], location_data)
        app.logger.info("User location inserted")
    except KeyError:
        Locations_db.new_input(location_data)
        app.logger.info("User location updated")
        
        
@socketio.on('get_locations')
def handle_get_locations(user_ids):
    app.logger.info(user_ids)
    locations = {}
    for user_id in user_ids:
        location_data = Locations_db.get_location_by_user_id(user_id)
        app.logger.info(location_data)
        if location_data:
            locations[user_id] = location_data['location']["coordinates"]
    app.logger.info(locations)
    emit('locations_update', locations)

        
if __name__ == "__main__":
    socketio.run(app, debug=True)