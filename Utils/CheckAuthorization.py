import jwt
from Models.adminModels import Admin_And_User
import logging
from flask import jsonify
import os
from dotenv import load_dotenv

load_dotenv()

class CheckAuthorization():
    def VerifyToken(token):
        try:
            if not token:
                return {"error": "Token is required"}, 401
            
            try:
                # Get JWT secret from environment variables
                secret_key = os.getenv("JWT_SECRET")
                if not secret_key:
                    logging.error("JWT_SECRET not found in environment variables")
                    return {"error": "Server configuration error"}, 500
                
                # Decode and verify the JWT token
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                
                # Check if user exists and token is valid
                user_id = decoded_token.get('user_id')
                if not user_id:
                    return {"error": "Invalid token format"}, 401
                
                user = Admin_And_User.objects(id=user_id).first()
                if not user:
                    return {"error": "User not found"}, 401
                
                # Check if token matches the user's stored token
                if user.auth_token != token:
                    return {"error": "Token mismatch"}, 401
                
                return True
                
            except jwt.ExpiredSignatureError as e:
                logging.error(f"Token Expired Error in verify_token: {str(e)}")
                return {"error": "Token has expired"}, 401
            except jwt.InvalidTokenError as e:
                logging.error(f"Invalid Token Error in verify_token: {str(e)}")
                return {"error": "Invalid token"}, 401
            except Exception as e:
                logging.error(f"JWT Decode Error in verify_token: {str(e)}")
                return {"error": "Token verification failed"}, 401
                
        except Exception as e:
            logging.error(f"Unexpected Error in verify_token: {str(e)}")
            return {"error": f"Authorization error: {str(e)}"}, 500
        
        