from flask import Flask, request, jsonify
from db.models import *
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from datetime import datetime
from flask_cors import CORS
from auth import authenticate_user, token_required
import jwt




app = Flask(__name__)
CORS(app, supports_credentials=True)


bcrypt = Bcrypt(app)
Users_db = Userdb()
Donations_requests_db = DonationRequestsdb()

SECRET_KEY = "bekkah"
app.config['SECRET_KEY'] = SECRET_KEY


@app.post('/api/register')
def register():
    body = request.get_json()
    app.logger.info(body)
    
    for value in body.values():
        if value == '':
            return {
                "status": "failed",
                "message": "Field missing!",
            }, 400
   
    if body["role"] == "donor":
        registration_details = {
        "first_name" : body["first_name"],
        "last_name" : body["last_name"],
        "email" : body["email"],
       "role" : body["role"],
       "password" : generate_password_hash("bekkah"),
       "date_approved": datetime.now(),
       "active": True
    }
    
    else:
        registration_details = {
        "first_name" : body["first_name"],
        "last_name" : body["last_name"],
        "email" : body["email"],
       "role" : body["role"],
       "password" : generate_password_hash("bekkah"),
       "status": "pending",
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
    except:
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
                "message": "Field missing!",
            }, 400
    
    email = body["email"]
    password = body["password"] 
    
    user_profile = authenticate_user(email, password)
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
                    "role": user_profile["role"]
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
            "message": "Unauthorized"
        }, 401


@app.get('/api/user')
@token_required
def current_user_profile(current_user):
    user_id = current_user["_id"]
    
    try:
        user = Users_db.get_user_by_id(user_id)
        app.logger.info(user)
        user["_id"] = str(user["_id"])
        del user["password"]
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "reponse": user
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
    
    details = {
        
    }
    
    try:
        Users_db.update_user_profile(user_id, details)
        user = Users_db.get_user_by_id(user_id)
                
        return {
            "status": "success",
            "message": "User profile updated successfully",
            "reponse": str(user["_id"])
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
        
        return {
            "status": "success",
            "message": "User profile fecthed successfully",
            "reponse": user
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
                "message": "Field missing!",
            }, 400

    
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
       'datetime_created': datetime.now()
   }
   
   try:
       request_id = Donations_requests_db.create_request(request_details)
       
       return {
           "status": "success",
           "message": "Donation request created",
           "response": {
               'request_id': str(request_id)
           }
       }, 200
       
       
   except:
       return {
           "status": "failed",
           "message": "Failed to create donation request"
       }, 500
 
@app.get('/api/donations')
@token_required
def get_all_donations(current_user):
    app.logger.info(current_user)
    
    try:
        request_details = list(Donations_requests_db.get_requests_by_donor_id(current_user["_id"]))
        
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
        
@app.delete('/api/donation/<donation_id>')
@token_required
def delete_donation(current_user, donation_id):
    donation = Donations_requests_db.get_specific_request(donation_id)
    
    if donation["status"] != "Pending":
        return {
            "status": "failed",
            "message": "Cannot delete request"
        }, 401
    
    try:
        deleted = Donations_requests_db.delete_request(donation_id)
        return {
            "status": "success",
            "message": "Donation request deleted"
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
        active_aggregators = list(Users_db.get_active_users_by_role("aggregator"))
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
        
        
@app.get('/api/pending-approvals')
@token_required
def get_pending_approvals(current_user):
    
    try:
        pending_approvals = list(Users_db.get_pending_approvals())
        app.logger.info(pending_approvals)
        for pending_approval in pending_approvals:
            pending_approval['_id'] = str(pending_approval['_id'])
            del pending_approval['password']
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
        
@app.get('/api/donations/active')
@token_required
def get_active_donations(current_user):
    
    try:
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
        active_aggregators = list(Users_db.get_active_users_by_role("aggregator"))
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
        approved = Users_db.update_user_profile_by_id(user_id, {"status": "Approved", "active": True})
        
        if approved:
            return {
                "status": "success",
                "message": "User approved successfully",
                "response": {
                    "status": "Approved" 
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
        
@app.patch('/api/user/<user_id>/reject')
@token_required
def reject(current_user, user_id):
    try:
        rejected = Users_db.update_user_profile_by_id(user_id, {"status": "Rejected"})
        
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
        

@app.get('/api/user/<user_id>')
@token_required
def get_user(current_user, user_id):
    
    try:
        user = Users_db.get_user_by_id(user_id)
        
        if user:
            user["_id"] = str(user["_id"])
            del user["password"]
            app.logger.info(user)
            return {
                "status": "success",
                "message": "User fetched successfully",
                "response": user
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
        disabled = Users_db.update_user_profile_by_id(user_id, {"active": False})

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
    




        
if __name__ == "__main__":
    app.run(debug=True)