from flask import request, jsonify
from Models.landModels import Land
from Models.adminModels import Admin_And_User
import jwt
import os
from datetime import datetime

class LandController:
    def create_land():
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Get the user
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Set status to pending for admin approval and associate with user
            data['status'] = 'pending'
            data['user'] = user
            
            # Set default values for required fields if not provided
            if 'property_type' not in data:
                data['property_type'] = 'land'
            if 'address' not in data:
                data['address'] = data.get('location', '')
            
            land = Land(**data)
            land.validate() 
            land.save()
            
            return jsonify({
                "message": "Land created successfully and pending approval",
                "land": land.to_json()
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def get_land():
        try:
            query = request.args.to_dict()
            if not query:
                # If no specific query, return all approved lands
                lands = Land.objects(status='available')
            else:
                lands = Land.objects(**query)
            
            return jsonify([land.to_json() for land in lands]), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def update_land():
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                user_id = payload.get('user_id')
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            land_id = request.args.get('id')
            if not land_id:
                return jsonify({"error": "Land ID is required"}), 400
            
            data = request.get_json()
            land = Land.objects(id=land_id).first()
            
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            # Check if user owns this land or is admin
            if str(land.user.id) != user_id and payload.get('role') != 'admin':
                return jsonify({"error": "Unauthorized to update this land"}), 403
            
            # Update land fields
            for key, value in data.items():
                if hasattr(land, key) and key not in ['user', 'created_at']:  # Don't allow updating these fields
                    setattr(land, key, value)
            
            land.updated_at = datetime.now()
            land.save()
            
            return jsonify({
                "message": "Land updated successfully",
                "land": land.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    def delete_land():
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
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
            
            # Check if user owns this land or is admin
            if str(land.user.id) != user_id and payload.get('role') != 'admin':
                return jsonify({"error": "Unauthorized to delete this land"}), 403
            
            land.delete()
            return jsonify({"message": "Land deleted successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        