from Models.adminModels import Admin_And_User
from Models.landModels import Land
from flask import request, jsonify
from datetime import datetime, timedelta
import jwt
import os

class AdminController:
    def get_all_users():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"success": False, "error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"success": False, "error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "error": "Invalid token"}), 401
            
            # Get all users
            users = Admin_And_User.objects()
            users_list = []
            for user in users:
                users_list.append({
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            return jsonify({"success": True, "data": {"users": users_list}}), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    def get_dashboard_stats():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            # Get dashboard statistics
            total_users = Admin_And_User.objects.count()
            total_lands = Land.objects.count()
            pending_lands = Land.objects(status='pending').count()
            available_lands = Land.objects(status='available').count()
            sold_lands = Land.objects(status='sold').count()
            
            # Get recent activities
            recent_lands = Land.objects().order_by('-created_at').limit(5)
            recent_users = Admin_And_User.objects().order_by('-created_at').limit(5)
            
            stats = {
                "total_users": total_users,
                "total_lands": total_lands,
                "pending_lands": pending_lands,
                "available_lands": available_lands,
                "sold_lands": sold_lands,
                "recent_lands": [land.to_json() for land in recent_lands],
                "recent_users": [user.to_json() for user in recent_users]
            }
            
            return jsonify(stats), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_pending_lands():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            # Get pending lands
            pending_lands = Land.objects(status='pending')
            lands_list = [land.to_json() for land in pending_lands]
            
            return jsonify(lands_list), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def approve_land():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            data = request.json
            land_id = data.get('land_id')
            status = data.get('status')  # 'approved' or 'rejected'
            
            if not land_id or not status:
                return jsonify({"error": "Land ID and status are required"}), 400
            
            if status not in ['approved', 'rejected']:
                return jsonify({"error": "Status must be 'approved' or 'rejected'"}), 400
            
            # Find and update land
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            land.status = status
            land.updated_at = datetime.now()
            land.save()
            
            return jsonify({
                "message": f"Land {status} successfully",
                "land": land.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def update_user():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            user_id = request.args.get('id')
            if not user_id:
                return jsonify({"error": "User ID is required"}), 400
            
            data = request.json
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Update user fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'role' in data:
                user.role = data['role']
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'password' in data:
                from werkzeug.security import generate_password_hash
                user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
            
            user.save()
            
            return jsonify({
                "message": "User updated successfully",
                "user": user.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def delete_user():
        try:
            # Check if user is admin
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Token required"}), 401
            
            # Verify token and check role
            try:
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Admin access required"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            
            user_id = request.args.get('id')
            if not user_id:
                return jsonify({"error": "User ID is required"}), 400
            
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Check if user is trying to delete themselves
            if str(user.id) == payload.get('user_id'):
                return jsonify({"error": "Cannot delete your own account"}), 400
            
            user.delete()
            
            return jsonify({"message": "User deleted successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
