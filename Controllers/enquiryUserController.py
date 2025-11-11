from flask import request, jsonify
from Models.enquiryModel import Enquiry
from Models.landModels import Land
from Models.adminModels import Admin_And_User
from Utils.CheckAuthorization import CheckAuthorization
from datetime import datetime, timezone
import jwt
import os


class EnquiryUserController:
    """
    User-side controller for Enquiries
    Users can create enquiries, view their own enquiries, update, and cancel
    """
    
    @staticmethod
    def create_enquiry():
        """
        Create a new enquiry for a land listing
        POST /api/user/enquiries/create
        Body: { land_id, enquiry_type, contact_name, contact_phone, contact_email, message?, budget?, preferred_contact_time? }
        """
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get user
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['land_id', 'enquiry_type', 'contact_name', 'contact_phone', 'contact_email']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"{field} is required"}), 400
            
            # Get land
            land = Land.objects(id=data['land_id']).first()
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            # Check if land is available
            if land.status != 'available':
                return jsonify({"error": "This land is not available for enquiry"}), 400
            
            # Validate enquiry type
            valid_types = ['buy_interest', 'site_visit', 'price_negotiation', 'general_enquiry']
            if data['enquiry_type'] not in valid_types:
                return jsonify({"error": f"enquiry_type must be one of: {', '.join(valid_types)}"}), 400
            
            # Create enquiry
            enquiry_data = {
                'user': user,
                'land': land,
                'enquiry_type': data['enquiry_type'],
                'contact_name': data['contact_name'],
                'contact_phone': data['contact_phone'],
                'contact_email': data['contact_email'],
                'message': data.get('message', ''),
                'budget': int(data['budget']) if data.get('budget') else None,
                'preferred_contact_time': data.get('preferred_contact_time', ''),
                'status': 'pending',
                'is_followed_up': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            enquiry = Enquiry(**enquiry_data)
            enquiry.validate()
            enquiry.save()
            
            return jsonify({
                "message": "Enquiry submitted successfully",
                "enquiry": enquiry.to_json()
            }), 201
            
        except ValueError as ve:
            return jsonify({"error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_my_enquiries():
        """
        Get all enquiries by authenticated user
        GET /api/user/enquiries/my-enquiries
        """
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get user
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Get all enquiries by this user
            enquiries = Enquiry.objects(user=user).order_by('-created_at')
            
            # Group by status
            grouped = {
                "pending": [],
                "contacted": [],
                "in_progress": [],
                "completed": [],
                "cancelled": []
            }
            
            for enquiry in enquiries:
                enquiry_json = enquiry.to_json()
                grouped[enquiry.status].append(enquiry_json)
            
            return jsonify({
                "success": True,
                "data": {
                    "total": enquiries.count(),
                    "grouped": grouped,
                    "enquiries": [e.to_json() for e in enquiries]
                }
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_enquiry_by_id():
        """
        Get a specific enquiry by ID (user can only view their own)
        GET /api/user/enquiries/enquiry?id=<enquiry_id>
        """
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Check ownership
            if str(enquiry.user.id) != user_id:
                return jsonify({"error": "Unauthorized to view this enquiry"}), 403
            
            return jsonify(enquiry.to_json()), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def update_enquiry():
        """
        Update user's own pending enquiry
        PUT /api/user/enquiries/update?id=<enquiry_id>
        Body: { contact_name?, contact_phone?, contact_email?, message?, budget?, preferred_contact_time? }
        """
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Check ownership
            if str(enquiry.user.id) != user_id:
                return jsonify({"error": "Unauthorized to update this enquiry"}), 403
            
            # Only allow updating pending enquiries
            if enquiry.status != 'pending':
                return jsonify({"error": f"Cannot update {enquiry.status} enquiries"}), 400
            
            # Get update data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Update allowed fields
            if 'contact_name' in data:
                enquiry.contact_name = data['contact_name']
            if 'contact_phone' in data:
                enquiry.contact_phone = data['contact_phone']
            if 'contact_email' in data:
                enquiry.contact_email = data['contact_email']
            if 'message' in data:
                enquiry.message = data['message']
            if 'budget' in data:
                enquiry.budget = int(data['budget']) if data['budget'] else None
            if 'preferred_contact_time' in data:
                enquiry.preferred_contact_time = data['preferred_contact_time']
            
            enquiry.updated_at = datetime.now(timezone.utc)
            enquiry.save()
            
            return jsonify({
                "message": "Enquiry updated successfully",
                "enquiry": enquiry.to_json()
            }), 200
            
        except ValueError as ve:
            return jsonify({"error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def cancel_enquiry():
        """
        Cancel user's own enquiry
        PUT /api/user/enquiries/cancel?id=<enquiry_id>
        """
        try:
            # Check authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Check ownership
            if str(enquiry.user.id) != user_id:
                return jsonify({"error": "Unauthorized to cancel this enquiry"}), 403
            
            # Cannot cancel completed enquiries
            if enquiry.status == 'completed':
                return jsonify({"error": "Cannot cancel completed enquiries"}), 400
            
            # Update status
            enquiry.status = 'cancelled'
            enquiry.updated_at = datetime.now(timezone.utc)
            enquiry.save()
            
            return jsonify({
                "message": "Enquiry cancelled successfully",
                "enquiry": enquiry.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def create_guest_enquiry():
        """
        Create a guest enquiry (no authentication required)
        POST /api/user/enquiries/guest-enquiry
        Body: { land_id, contact_phone }
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            if 'land_id' not in data or not data['land_id']:
                return jsonify({"error": "land_id is required"}), 400
            if 'contact_phone' not in data or not data['contact_phone']:
                return jsonify({"error": "contact_phone is required"}), 400
            
            # Get land
            land = Land.objects(id=data['land_id']).first()
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            # Check if land is available
            if land.status != 'available':
                return jsonify({"error": "This land is not available for enquiry"}), 400
            
            # Create guest enquiry
            enquiry_data = {
                'user': None,
                'land': land,
                'is_guest': True,
                'enquiry_type': 'buy_interest',
                'contact_name': data.get('contact_name', 'Guest User'),
                'contact_phone': data['contact_phone'],
                'contact_email': data.get('contact_email', ''),
                'message': data.get('message', 'Guest enquiry - interested in this property'),
                'budget': None,
                'preferred_contact_time': '',
                'status': 'pending',
                'is_followed_up': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            enquiry = Enquiry(**enquiry_data)
            enquiry.validate()
            enquiry.save()
            
            return jsonify({
                "message": "Guest enquiry submitted successfully",
                "enquiry": enquiry.to_json()
            }), 201
            
        except ValueError as ve:
            return jsonify({"error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_available_lands():
        """
        Get all available lands for browsing (public endpoint for authenticated users)
        GET /api/user/enquiries/available-lands
        Query params: property_type?, location?, min_price?, max_price?, min_size?, max_size?, search?
        """
        try:
            # Build query filters
            filters = {'status': 'available'}
            
            # Log incoming parameters for debugging
            print(f"Received query params: {dict(request.args)}")
            
            # Property type filter
            property_type = request.args.get('property_type')
            if property_type and property_type != '':
                filters['property_type'] = property_type
                print(f"Applied property_type filter: {property_type}")
            
            # Location filter (case-insensitive partial match)
            location = request.args.get('location')
            if location:
                filters['location__icontains'] = location
            
            # Price range filter
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            if min_price:
                filters['price__gte'] = int(min_price)
            if max_price:
                filters['price__lte'] = int(max_price)
            
            # Size range filter
            min_size = request.args.get('min_size')
            max_size = request.args.get('max_size')
            if min_size:
                filters['size__gte'] = int(min_size)
            if max_size:
                filters['size__lte'] = int(max_size)
            
            # Search parameter (searches across title, location, description)
            search = request.args.get('search')
            if search:
                from mongoengine import Q
                search_query = Q(title__icontains=search) | Q(location__icontains=search) | Q(description__icontains=search)
                lands = Land.objects(search_query, **filters)
            else:
                # Get lands with filters
                lands = Land.objects(**filters)
            
            # Order by created date
            lands = lands.order_by('-created_at')
            
            # Log final results
            print(f"Applied filters: {filters}")
            print(f"Found {lands.count()} lands")
            
            return jsonify({
                "total": lands.count(),
                "lands": [land.to_json() for land in lands]
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_land_by_id(land_id):
        """
        Get land details by ID (public endpoint)
        GET /api/user/enquiries/land/<land_id>
        """
        try:
            # Get land by ID
            land = Land.objects(id=land_id).first()
            
            if not land:
                return jsonify({"error": "Land not found"}), 404
            
            # Only return available lands to public
            if land.status != 'available':
                return jsonify({"error": "Land not available"}), 404
            
            return jsonify({
                "success": True,
                "land": land.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
