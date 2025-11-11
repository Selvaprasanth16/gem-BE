from flask import request, jsonify
from Models.sellLandModel import SellLandSubmission
from Models.landModels import Land
from Models.adminModels import Admin_And_User
from Utils.CheckAuthorization import CheckAuthorization
from datetime import datetime, timezone
import jwt
import os


class SellLandAdminController:
    """
    Admin-side controller for Sell Your Land form submissions
    Admins can view all submissions, approve/reject, move to Land model, update, and delete
    """
    
    @staticmethod
    def verify_admin():
        """Helper method to verify admin authentication"""
        token = request.headers.get('token')
        if not token:
            return None, (jsonify({"error": "Authentication required"}), 401)
        
        verify = CheckAuthorization.VerifyToken(token)
        if verify != True:
            return None, verify
        
        # Decode token and check role
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return None, (jsonify({"error": "Admin access required"}), 403)
            return payload, None
        except Exception as e:
            return None, (jsonify({"error": "Token verification failed"}), 401)
    
    @staticmethod
    def get_all_submissions():
        """
        Get all sell land submissions with optional filters
        GET /api/admin/sell-land/all
        Query params: status?, land_type?, user_id?, start_date?, end_date?
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Build query filters
            filters = {}
            
            # Status filter (exclude 'all' from filtering)
            status = request.args.get('status')
            if status and status != 'all':
                filters['status'] = status
            
            # Land type filter
            land_type = request.args.get('land_type')
            if land_type:
                filters['land_type'] = land_type
            
            # User filter
            user_id = request.args.get('user_id')
            if user_id:
                user = Admin_And_User.objects(id=user_id).first()
                if user:
                    filters['user'] = user
            
            # Date range filter
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            if start_date:
                filters['created_at__gte'] = datetime.fromisoformat(start_date)
            if end_date:
                filters['created_at__lte'] = datetime.fromisoformat(end_date)
            
            # Get submissions with filters
            submissions = SellLandSubmission.objects(**filters).order_by('-created_at')
            
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
    def get_pending_submissions():
        """
        Get all pending submissions
        GET /api/admin/sell-land/pending
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get pending submissions
            pending = SellLandSubmission.objects(status='pending').order_by('-created_at')
            
            return jsonify({
                "total": pending.count(),
                "submissions": [s.to_json() for s in pending]
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_submission_by_id():
        """
        Get any submission by ID (admin can view all)
        GET /api/admin/sell-land/submission?id=<submission_id>
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            return jsonify(submission.to_json()), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def approve_submission():
        """
        Approve a submission (changes status to approved)
        POST /api/admin/sell-land/approve
        Body: { submission_id }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            submission_id = data.get('submission_id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Update status
            submission.status = 'approved'
            submission.approved_at = datetime.now(timezone.utc)
            submission.updated_at = datetime.now(timezone.utc)
            submission.save()
            
            return jsonify({
                "message": "Submission approved successfully",
                "submission": submission.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def reject_submission():
        """
        Reject a submission
        POST /api/admin/sell-land/reject
        Body: { submission_id, reason? }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            submission_id = data.get('submission_id')
            reason = data.get('reason', 'Does not meet requirements')
            
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Update status
            submission.status = 'rejected'
            submission.rejection_reason = reason
            submission.rejected_at = datetime.now(timezone.utc)
            submission.updated_at = datetime.now(timezone.utc)
            submission.save()
            
            return jsonify({
                "message": "Submission rejected",
                "reason": reason,
                "submission": submission.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def move_to_land():
        """
        Move approved submission to Land model
        POST /api/admin/sell-land/move-to-land
        Body: { submission_id, additional_data? }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            submission_id = data.get('submission_id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Check if already moved
            if submission.status == 'moved_to_land':
                return jsonify({"error": "Submission already moved to Land model"}), 400
            
            # Map land_type to property_type and features
            land_type_mapping = {
                'Coconut Land': {'property_type': 'farm', 'features': ['agricultural', 'Coconut Farm']},
                'Empty Land': {'property_type': 'land', 'features': []},
                'Commercial Land': {'property_type': 'commercial', 'features': ['commercial']},
                'House': {'property_type': 'residential', 'features': ['residential']}
            }
            
            mapping = land_type_mapping.get(submission.land_type, {'property_type': 'land', 'features': []})
            
            # Create Land object from submission
            land_data = {
                'user': submission.user,
                'title': data.get('title', f"{submission.land_type} - {submission.location[:50]}"),
                'location': submission.location,
                'size': submission.area,
                'price': submission.price,
                'status': 'available',  # Set as available when moved
                'description': data.get('description', submission.description or f"{submission.land_type} for sale"),
                'property_type': mapping['property_type'],
                'address': submission.location,
                'contact_phone': submission.contact_phone,
                'contact_email': submission.user.email,
                'features': mapping['features'],
                'images_urls': data.get('images_urls', []),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            # Create and save land
            land = Land(**land_data)
            land.validate()
            land.save()
            
            # Update submission status
            submission.status = 'moved_to_land'
            submission.moved_to_land_id = str(land.id)
            submission.updated_at = datetime.now(timezone.utc)
            submission.save()
            
            return jsonify({
                "message": "Submission successfully moved to Land model",
                "submission": submission.to_json(),
                "land": land.to_json()
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def update_submission():
        """
        Update any submission field
        PUT /api/admin/sell-land/update?id=<submission_id>
        Body: { owner_name?, contact_phone?, location?, price?, area?, land_type?, status?, description? }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Get update data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Update fields
            if 'owner_name' in data:
                submission.owner_name = data['owner_name']
            if 'contact_phone' in data:
                submission.contact_phone = data['contact_phone']
            if 'location' in data:
                submission.location = data['location']
            if 'price' in data:
                submission.price = int(data['price'])
            if 'area' in data:
                submission.area = int(data['area'])
            if 'land_type' in data:
                valid_types = ['Coconut Land', 'Empty Land', 'Commercial Land', 'House']
                if data['land_type'] in valid_types:
                    submission.land_type = data['land_type']
            if 'status' in data:
                valid_statuses = ['pending', 'approved', 'rejected', 'moved_to_land']
                if data['status'] in valid_statuses:
                    submission.status = data['status']
            if 'description' in data:
                submission.description = data['description']
            if 'rejection_reason' in data:
                submission.rejection_reason = data['rejection_reason']
            
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
        Delete any submission
        DELETE /api/admin/sell-land/delete?id=<submission_id>
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get submission ID
            submission_id = request.args.get('id')
            if not submission_id:
                return jsonify({"error": "Submission ID is required"}), 400
            
            # Get submission
            submission = SellLandSubmission.objects(id=submission_id).first()
            if not submission:
                return jsonify({"error": "Submission not found"}), 404
            
            # Store info before deletion
            submission_info = {
                "id": str(submission.id),
                "owner_name": submission.owner_name,
                "land_type": submission.land_type
            }
            
            # Delete submission
            submission.delete()
            
            return jsonify({
                "message": "Submission deleted successfully",
                "deleted_submission": submission_info
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get dashboard statistics for sell land submissions
        GET /api/admin/sell-land/dashboard-stats
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get counts
            total_submissions = SellLandSubmission.objects.count()
            pending_submissions = SellLandSubmission.objects(status='pending').count()
            approved_submissions = SellLandSubmission.objects(status='approved').count()
            rejected_submissions = SellLandSubmission.objects(status='rejected').count()
            moved_submissions = SellLandSubmission.objects(status='moved_to_land').count()
            
            # Get counts by land type
            land_type_stats = {}
            for land_type in ['Coconut Land', 'Empty Land', 'Commercial Land', 'House']:
                land_type_stats[land_type] = SellLandSubmission.objects(land_type=land_type).count()
            
            # Get recent submissions
            recent_submissions = SellLandSubmission.objects().order_by('-created_at').limit(10)
            recent_pending = SellLandSubmission.objects(status='pending').order_by('-created_at').limit(5)
            
            stats = {
                "overview": {
                    "total_submissions": total_submissions,
                    "pending_submissions": pending_submissions,
                    "approved_submissions": approved_submissions,
                    "rejected_submissions": rejected_submissions,
                    "moved_submissions": moved_submissions
                },
                "by_land_type": land_type_stats,
                "recent_submissions": [s.to_json() for s in recent_submissions],
                "pending_approvals": [s.to_json() for s in recent_pending]
            }
            
            return jsonify(stats), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def bulk_approve():
        """
        Approve multiple submissions at once
        POST /api/admin/sell-land/bulk-approve
        Body: { submission_ids: [id1, id2, ...] }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            submission_ids = data.get('submission_ids', [])
            if not submission_ids:
                return jsonify({"error": "Submission IDs are required"}), 400
            
            # Approve all submissions
            approved_count = 0
            failed = []
            
            for submission_id in submission_ids:
                try:
                    submission = SellLandSubmission.objects(id=submission_id).first()
                    if submission:
                        submission.status = 'approved'
                        submission.approved_at = datetime.now(timezone.utc)
                        submission.updated_at = datetime.now(timezone.utc)
                        submission.save()
                        approved_count += 1
                    else:
                        failed.append({"id": submission_id, "reason": "Not found"})
                except Exception as e:
                    failed.append({"id": submission_id, "reason": str(e)})
            
            return jsonify({
                "message": "Bulk approval completed",
                "approved": approved_count,
                "failed": len(failed),
                "failed_details": failed
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def bulk_delete():
        """
        Delete multiple submissions at once
        POST /api/admin/sell-land/bulk-delete
        Body: { submission_ids: [id1, id2, ...] }
        """
        try:
            # Verify admin
            payload, error = SellLandAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            submission_ids = data.get('submission_ids', [])
            if not submission_ids:
                return jsonify({"error": "Submission IDs are required"}), 400
            
            # Delete all submissions
            deleted_count = 0
            failed = []
            
            for submission_id in submission_ids:
                try:
                    submission = SellLandSubmission.objects(id=submission_id).first()
                    if submission:
                        submission.delete()
                        deleted_count += 1
                    else:
                        failed.append({"id": submission_id, "reason": "Not found"})
                except Exception as e:
                    failed.append({"id": submission_id, "reason": str(e)})
            
            return jsonify({
                "message": "Bulk deletion completed",
                "deleted": deleted_count,
                "failed": len(failed),
                "failed_details": failed
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
