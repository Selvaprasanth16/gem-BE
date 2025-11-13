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
            # Normalize features to list of allowed values
            allowed_features = {'residential', 'commercial', 'agricultural', 'Coconut Farm'}
            raw_features = data.get('features', [])
            if isinstance(raw_features, str):
                raw_features = [raw_features]
            elif not isinstance(raw_features, list):
                raw_features = []
            # Map common variants
            feature_map = {
                'coconut land': 'Coconut Farm',
                'coconut farm': 'Coconut Farm',
                'farm': 'Coconut Farm',
            }
            norm_features = []
            for f in raw_features:
                if not isinstance(f, str):
                    continue
                key = f.strip()
                mapped = feature_map.get(key.lower(), key)
                if mapped in allowed_features:
                    norm_features.append(mapped)

            # Parse coordinates if provided (supports "lat,lon" or Google Maps URL containing @lat,lon or q=lat,lon)
            def parse_coordinates(val):
                try:
                    if not val or not isinstance(val, str):
                        return None, None
                    s = val.strip()
                    # If full URL, try to find @lat,lon or q=lat,lon
                    if 'http' in s:
                        import re
                        m = re.search(r'@\s*([-+]?\d+\.?\d*)\s*,\s*([-+]?\d+\.?\d*)', s)
                        if not m:
                            m = re.search(r'[?&]q=\s*([-+]?\d+\.?\d*)\s*,\s*([-+]?\d+\.?\d*)', s)
                        if m:
                            return float(m.group(1)), float(m.group(2))
                    # plain "lat,lon"
                    if ',' in s:
                        lat_s, lon_s = [p.strip() for p in s.split(',', 1)]
                        return float(lat_s), float(lon_s)
                except Exception:
                    return None, None
                return None, None

            coord_lat, coord_lon = parse_coordinates(data.get('coordinates'))

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
                'features': norm_features,
                'contact_phone': data.get('contact_phone', ''),
                'contact_email': data.get('contact_email', ''),
                'latitude': data.get('latitude') if data.get('latitude') is not None else coord_lat,
                'longitude': data.get('longitude') if data.get('longitude') is not None else coord_lon,
                # urgent
                'is_urgent': True if (str(data.get('is_urgent')).lower() in ['true','1','yes']) else False,
                'urgent_priority': int(data.get('urgent_priority', 0) or 0),
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
            
            data = request.json or {}
            # Prefer query param (?id=) but support legacy JSON body land_id
            land_id = request.args.get('id') or data.get('land_id')
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
            
            data = request.json or {}
            land_id = request.args.get('id') or data.get('land_id')
            
            if not land_id:
                return jsonify({"success": False, "error": "Missing land id. Pass ?id=<land_id> in query (preferred) or include 'land_id' in body for backward compatibility."}), 400
            
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
                allowed_features = {'residential', 'commercial', 'agricultural', 'Coconut Farm'}
                raw = data.get('features')
                if isinstance(raw, str):
                    raw = [raw]
                elif not isinstance(raw, list):
                    raw = []
                feature_map = {
                    'coconut land': 'Coconut Farm',
                    'coconut farm': 'Coconut Farm',
                    'farm': 'Coconut Farm',
                }
                norm = []
                for f in raw:
                    if not isinstance(f, str):
                        continue
                    key = f.strip()
                    mapped = feature_map.get(key.lower(), key)
                    if mapped in allowed_features:
                        norm.append(mapped)
                land.features = norm
            if 'contact_phone' in data:
                land.contact_phone = data['contact_phone']
            if 'contact_email' in data:
                land.contact_email = data['contact_email']
            # Urgent fields
            if 'is_urgent' in data:
                land.is_urgent = True if (str(data.get('is_urgent')).lower() in ['true','1','yes']) else False
            if 'urgent_priority' in data and data.get('urgent_priority') is not None:
                try:
                    land.urgent_priority = int(data.get('urgent_priority'))
                except Exception:
                    pass
            # Coordinates parsing for update
            def parse_coordinates(val):
                try:
                    if not val or not isinstance(val, str):
                        return None, None
                    s = val.strip()
                    if 'http' in s:
                        import re
                        m = re.search(r'@\s*([-+]?\d+\.?\d*)\s*,\s*([-+]?\d+\.?\d*)', s)
                        if not m:
                            m = re.search(r'[?&]q=\s*([-+]?\d+\.?\d*)\s*,\s*([-+]?\d+\.?\d*)', s)
                        if m:
                            return float(m.group(1)), float(m.group(2))
                    if ',' in s:
                        lat_s, lon_s = [p.strip() for p in s.split(',', 1)]
                        return float(lat_s), float(lon_s)
                except Exception:
                    return None, None
                return None, None

            if 'coordinates' in data and data.get('coordinates'):
                lat, lon = parse_coordinates(data.get('coordinates'))
                if lat is not None and lon is not None:
                    land.latitude = lat
                    land.longitude = lon
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
