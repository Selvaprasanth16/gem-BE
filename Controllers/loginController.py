from Models.adminModels import Admin_And_User
from flask import request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import jwt
import os
from mongoengine.queryset.visitor import Q

class LoginController:
    def login():
        try:
            data = request.json
            # Support login ONLY via email or phone (no username)
            identifier = data.get('identifier') or data.get('email') or data.get('phone')
            password = data.get('password')
            
            if not identifier or not password:
                return jsonify({"error": "Email or mobile and password are required"}), 400
            
            # Find user by email OR phone only
            user = Admin_And_User.objects(
                Q(email=identifier) | Q(phone=identifier)
            ).first()
            if not user:
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Check password
            if not check_password_hash(user.password, password):
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Generate JWT token
            payload = {
                "user_id": str(user.id),
                "username": user.username,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", 60)))
            }
            
            token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))
            
            # Update user's auth_token
            user.auth_token = token
            user.save()
            
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "phone": getattr(user, 'phone', None),
                    "role": user.role,
                    "full_name": user.full_name
                }
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def change_password():
        try:
            data = request.json
            username = data.get('username')
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not username or not old_password or not new_password:
                return jsonify({"error": "Username, old password, and new password are required"}), 400
            
            # Find user by username
            user = Admin_And_User.objects(username=username).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Check old password
            if not check_password_hash(user.password, old_password):
                return jsonify({"error": "Invalid old password"}), 401
            
            # Update password
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.save()
            
            return jsonify({"message": "Password changed successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
