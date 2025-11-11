from Models.landModels import Land
from Models.adminModels import Admin_And_User
from flask import request, jsonify
from datetime import datetime
from Utils.CheckAuthorization import CheckAuthorization
from Utils.cloudinaryUpload import CloudinaryUpload
import jwt
import os

class LandAdminController:
    
    @staticmethod
    def verify_admin():
        """Verify if user is admin"""
        token = request.headers.get('token')
        if not token:
            return None, (jsonify({"success": False, "error": "Token required"}), 401)
        
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return None, (jsonify({"success": False, "error": "Admin access required"}), 403)
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, (jsonify({"success": False, "error": "Token expired"}), 401)
        except jwt.InvalidTokenError:
            return None, (jsonify({"success": False, "error": "Invalid token"}), 401)
    
    @staticmethod
    def create_land():
        """
        Create a new land listing
        POST /api/admin/lands/create
        Body: { title, location, property_type, price, size, description? }
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            data = request.json
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['title', 'location', 'property_type', 'price', 'size', 'address']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"success": False, "error": f"{field} is required"}), 400
            
            # Validate property type - map frontend values to model values
            property_type_map = {
                'Coconut Land': 'farm',
                'Empty Land': 'land',
                'Commercial Land': 'commercial',
                'House': 'residential'
            }
            
            if data['property_type'] not in property_type_map:
                return jsonify({"success": False, "error": f"property_type must be one of: {', '.join(property_type_map.keys())}"}), 400
            
            # Get admin user
            admin_user = Admin_And_User.objects(id=payload['user_id']).first()
            if not admin_user:
                return jsonify({"success": False, "error": "Admin user not found"}), 404
            
            # Create land
            land_data = {
                'user': admin_user,
                'title': data['title'],
                'location': data['location'],
                'property_type': property_type_map[data['property_type']],
                'price': int(data['price']),
                'size': int(data['size']),
                'description': data.get('description', ''),
                'address': data['address'],
                'status': 'available',
                'images_urls': data.get('images_urls', []),
                'features': data.get('features', []),
                'contact_phone': data.get('contact_phone', ''),
                'contact_email': data.get('contact_email', ''),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            land = Land(**land_data)
            land.validate()
            land.save()
            
            return jsonify({
                "success": True,
                "message": "Land created successfully",
                "data": {"land": land.to_json()}
            }), 201
            
        except ValueError as ve:
            return jsonify({"success": False, "error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @staticmethod
    def get_all_lands():
        """
        Get all lands with optional filters
        GET /api/admin/lands/all
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            # Build query filters
            filters = {}
            
            # Status filter (exclude 'all' from filtering)
            status = request.args.get('status')
            if status and status != 'all':
                filters['status'] = status
            
            # Property type filter
            property_type = request.args.get('property_type')
            if property_type:
                filters['property_type'] = property_type
            
            # Get lands with filters
            lands = Land.objects(**filters).order_by('-created_at')
            
            # Group by status
            grouped = {
                "available": [],
                "sold": [],
                "pending": [],
                "rejected": []
            }
            
            for land in lands:
                land_json = land.to_json()
                grouped[land.status].append(land_json)
            
            return jsonify({
                "success": True,
                "data": {
                    "total": lands.count(),
                    "grouped": grouped,
                    "lands": [land.to_json() for land in lands]
                }
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @staticmethod
    def update_land_status():
        """
        Update land status (mark as sold, available, etc.)
        PUT /api/admin/lands/update-status
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            data = request.json
            land_id = data.get('land_id')
            new_status = data.get('status')
            
            if not land_id or not new_status:
                return jsonify({"success": False, "error": "land_id and status are required"}), 400
            
            # Validate status
            valid_statuses = ['available', 'sold', 'pending', 'rejected']
            if new_status not in valid_statuses:
                return jsonify({"success": False, "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
            
            # Get land
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"success": False, "error": "Land not found"}), 404
            
            # Update status
            land.status = new_status
            land.updated_at = datetime.utcnow()
            land.save()
            
            return jsonify({
                "success": True,
                "message": f"Land status updated to {new_status}",
                "data": {"land": land.to_json()}
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @staticmethod
    def update_land():
        """
        Update land details
        PUT /api/admin/lands/update
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            data = request.json
            land_id = data.get('land_id')
            
            if not land_id:
                return jsonify({"success": False, "error": "land_id is required"}), 400
            
            # Get land
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"success": False, "error": "Land not found"}), 404
            
            # Property type mapping
            property_type_map = {
                'Coconut Land': 'farm',
                'Empty Land': 'land',
                'Commercial Land': 'commercial',
                'House': 'residential'
            }
            
            # Update fields
            if 'title' in data:
                land.title = data['title']
            if 'description' in data:
                land.description = data['description']
            if 'price' in data:
                land.price = int(data['price'])
            if 'size' in data:
                land.size = int(data['size'])
            if 'location' in data:
                land.location = data['location']
            if 'address' in data:
                land.address = data['address']
            if 'property_type' in data:
                # Map frontend value to model value
                land.property_type = property_type_map.get(data['property_type'], data['property_type'])
            if 'status' in data:
                land.status = data['status']
            if 'images_urls' in data:
                land.images_urls = data['images_urls']
            if 'features' in data:
                land.features = data['features']
            if 'contact_phone' in data:
                land.contact_phone = data['contact_phone']
            if 'contact_email' in data:
                land.contact_email = data['contact_email']
            if 'latitude' in data:
                land.latitude = data['latitude']
            if 'longitude' in data:
                land.longitude = data['longitude']
            
            land.updated_at = datetime.utcnow()
            land.save()
            
            return jsonify({
                "success": True,
                "message": "Land updated successfully",
                "data": {"land": land.to_json()}
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @staticmethod
    def delete_land():
        """
        Delete a land
        DELETE /api/admin/lands/delete?id=<land_id>
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            land_id = request.args.get('id')
            if not land_id:
                return jsonify({"success": False, "error": "Land ID is required"}), 400
            
            # Get land
            land = Land.objects(id=land_id).first()
            if not land:
                return jsonify({"success": False, "error": "Land not found"}), 404
            
            # Attempt to delete Cloudinary images first (best-effort)
            deleted_images = []
            failed_images = []
            try:
                for url in land.images_urls or []:
                    try:
                        res = CloudinaryUpload.delete_image_by_url(url)
                        # Cloudinary returns {'result': 'ok'} on success, 'not found' if already gone
                        if isinstance(res, dict) and res.get('result') in ['ok', 'not found']:
                            deleted_images.append(url)
                        else:
                            failed_images.append({"url": url, "response": res})
                    except Exception as ex:
                        failed_images.append({"url": url, "error": str(ex)})
            except Exception:
                # Continue even if bulk deletion loop had unexpected error
                pass

            # Delete land record
            land.delete()
            
            return jsonify({
                "success": True,
                "message": "Land deleted successfully",
                "data": {
                    "deleted_images_count": len(deleted_images),
                    "failed_images_count": len(failed_images),
                    "failed_images": failed_images[:5]  # cap to avoid huge payloads
                }
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get lands dashboard statistics
        GET /api/admin/lands/dashboard-stats
        """
        try:
            # Verify admin
            payload, error = LandAdminController.verify_admin()
            if error:
                return error
            
            # Get statistics
            total_lands = Land.objects().count()
            available_lands = Land.objects(status='available').count()
            sold_lands = Land.objects(status='sold').count()
            pending_lands = Land.objects(status='pending').count()
            rejected_lands = Land.objects(status='rejected').count()
            
            # Get recent lands
            recent_lands = Land.objects().order_by('-created_at').limit(5)
            
            stats = {
                "overview": {
                    "total_lands": total_lands,
                    "available_lands": available_lands,
                    "sold_lands": sold_lands,
                    "pending_lands": pending_lands,
                    "rejected_lands": rejected_lands
                },
                "recent_lands": [land.to_json() for land in recent_lands]
            }
            
            return jsonify({
                "success": True,
                "data": stats
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
