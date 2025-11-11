from flask import request, jsonify
from Models.sellLandModel import SellLandSubmission
from Models.adminModels import Admin_And_User
from Utils.CheckAuthorization import CheckAuthorization
from datetime import datetime, timezone


class SellLandUserController:
    """
    User-side controller for Sell Your Land form submissions
    Users can create, view their own submissions, update pending submissions, and delete
    """
    
    @staticmethod
    def create_submission():
        """
        Create a new sell land form submission
        POST /api/user/sell-land/create
        Body: { name, phone, location, price, area, landType, description? }
        """
        try:
            # Check authentication using CheckAuthorization
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token to get user_id
            import jwt
            import os
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get user
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Get form data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['name', 'phone', 'location', 'price', 'area', 'landType']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"{field} is required"}), 400
            
            # Validate landType
            valid_land_types = ['Coconut Land', 'Empty Land', 'Commercial Land', 'House']
            if data['landType'] not in valid_land_types:
                return jsonify({"error": f"landType must be one of: {', '.join(valid_land_types)}"}), 400
            
            # Create submission
            submission_data = {
                'user': user,
                'owner_name': data['name'],
                'contact_phone': data['phone'],
                'location': data['location'],
                'price': int(data['price']),
                'area': int(data['area']),
                'land_type': data['landType'],
                'status': 'pending',
                'description': data.get('description', ''),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            submission = SellLandSubmission(**submission_data)
            submission.validate()
            submission.save()
            
            return jsonify({
                "message": "Land submission created successfully and pending admin approval",
                "submission": submission.to_json()
            }), 201
            
        except ValueError as ve:
            return jsonify({"error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_my_submissions():
        """
        Get all submissions by authenticated user
        GET /api/user/sell-land/my-submissions
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
            import jwt
            import os
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get user
            user = Admin_And_User.objects(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Get all submissions by this user
            submissions = SellLandSubmission.objects(user=user).order_by('-created_at')
            
            # Group by status
            grouped = {
                "pending": [],
                "approved": [],
                "rejected": [],
                "moved_to_land": []
            }
            
            for submission in submissions:
                submission_json = submission.to_json()
                grouped[submission.status].append(submission_json)
            
            return jsonify({
                "success": True,
                "data": {
                    "total": submissions.count(),
                    "grouped": grouped,
                    "submissions": [s.to_json() for s in submissions]
                }
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_submission_by_id():
        """
        Get a specific submission by ID (user can only view their own)
        GET /api/user/sell-land/submission?id=<submission_id>
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
            import jwt
            import os
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Check ownership
            if str(submission.user.id) != user_id:
                return jsonify({"error": "Unauthorized to view this submission"}), 403
            
            return jsonify(submission.to_json()), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def update_submission():
        """
        Update user's own pending submission
        PUT /api/user/sell-land/update?id=<submission_id>
        Body: { name?, phone?, location?, price?, area?, description? }
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
            import jwt
            import os
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Check ownership
            if str(submission.user.id) != user_id:
                return jsonify({"error": "Unauthorized to update this submission"}), 403
            
            # Only allow updating pending submissions
            if submission.status != 'pending':
                return jsonify({"error": f"Cannot update {submission.status} submissions"}), 400
            
            # Get update data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Update allowed fields
            if 'name' in data:
                submission.owner_name = data['name']
            if 'phone' in data:
                submission.contact_phone = data['phone']
            if 'location' in data:
                submission.location = data['location']
            if 'price' in data:
                submission.price = int(data['price'])
            if 'area' in data:
                submission.area = int(data['area'])
            if 'description' in data:
                submission.description = data['description']
            
            submission.updated_at = datetime.now(timezone.utc)
            submission.save()
            
            return jsonify({
                "message": "Submission updated successfully",
                "submission": submission.to_json()
            }), 200
            
        except ValueError as ve:
            return jsonify({"error": f"Invalid data: {str(ve)}"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def delete_submission():
        """
        Delete user's own submission
        DELETE /api/user/sell-land/delete?id=<submission_id>
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
            import jwt
            import os
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            user_id = payload.get('user_id')
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Check ownership
            if str(submission.user.id) != user_id:
                return jsonify({"error": "Unauthorized to delete this submission"}), 403
            
            # Delete submission
            submission.delete()
            
            return jsonify({"message": "Submission deleted successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
