from Models.adminModels import Admin_And_User
from Models.landModels import Land
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os

class UserController:
    def create_user():
        try:
            data = request.json

            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

            user = Admin_And_User(
                username=data['username'],
                email=data['email'],
                password=hashed_password,
                role=data.get('role', 'user'),  # Default to 'user' if not specified
                full_name=data['full_name']
            )
            user.save()

            payload = {
                "user_id": str(user.id),
                "username": user.username,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", 60)))
            }

            token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))

            return jsonify({
                "message": "User created successfully",
                "token": token
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def get_user():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            return jsonify(user.to_json()), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def update_user():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            data = request.json

            # Only hash if password is being updated
            if data.get('password'):
                user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.full_name = data.get('full_name', user.full_name)
            # Allow updating optional phone
            if 'phone' in data:
                user.phone = data.get('phone')

            user.save()

            return jsonify({"message": "User updated successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def delete_user():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            user.delete()
            return jsonify({"message": "User deleted successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def get_my_lands():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            # Get lands created by this user (you might want to add a user_id field to Land model)
            # For now, we'll return all lands with status 'pending' or 'approved'
            user_lands = Land.objects(status__in=['pending', 'available', 'sold'])
            lands_list = [land.to_json() for land in user_lands]
            
            return jsonify(lands_list), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def get_user_dashboard():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            # Get user's lands statistics
            total_lands = Land.objects.count()  # This should be filtered by user_id when model is updated
            pending_lands = Land.objects(status='pending').count()
            available_lands = Land.objects(status='available').count()
            sold_lands = Land.objects(status='sold').count()
            
            stats = {
                "total_lands": total_lands,
                "pending_lands": pending_lands,
                "available_lands": available_lands,
                "sold_lands": sold_lands
            }
            
            return jsonify(stats), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def submit_land():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Set status to pending for admin approval
            data['status'] = 'pending'
            
            land = Land(**data)
            land.validate()
            land.save()
            
            return jsonify({
                "message": "Land submitted successfully and pending approval",
                "land": land.to_json()
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def update_my_land():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            land_id = request.args.get('id')
            if not land_id:
                return jsonify({"error": "Land ID is required"}), 400
            
            data = request.json
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            # Update land fields
            for key, value in data.items():
                if hasattr(land, key):
                    setattr(land, key, value)
            
            land.updated_at = datetime.now()
            land.save()
            
            return jsonify({
                "message": "Land updated successfully",
                "land": land.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def delete_my_land():
        try:
            user_token = request.headers.get('token')
            if not user_token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(user_token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 400
            
            land_id = request.args.get('id')
            if not land_id:
                return jsonify({"error": "Land ID is required"}), 400
            
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            land.delete()
            
            return jsonify({"message": "Land deleted successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
