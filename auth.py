from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from db.models import *
from functools import wraps
import jwt
from flask import request, abort
from flask import current_app

User_db = Userdb()

def authenticate_user(email, pwd):
    user_profile = User_db.get_user_by_email(email)
    
    if user_profile: 
        authenticated = check_password_hash(user_profile["password"], pwd)
        if authenticated and user_profile["active"]:
            return user_profile

        else:
            return False
        
    else:
        return "not found"
    



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            print(token)
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user=User_db.get_user_by_id(data["user_id"])
            if current_user is None:
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated