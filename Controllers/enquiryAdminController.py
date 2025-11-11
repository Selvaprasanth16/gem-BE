from flask import request, jsonify
from Models.enquiryModel import Enquiry
from Models.landModels import Land
from Models.adminModels import Admin_And_User
from Utils.CheckAuthorization import CheckAuthorization
from datetime import datetime, timezone
import jwt
import os


class EnquiryAdminController:
    """
    Admin-side controller for Enquiries
    Admins can view all enquiries, update status, add notes, manage follow-ups
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
    def get_all_enquiries():
        """
        Get all enquiries with optional filters
        GET /api/admin/enquiries/all
        Query params: status?, enquiry_type?, user_id?, land_id?, start_date?, end_date?, is_followed_up?
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Build query filters
            filters = {}
            
            # Status filter (exclude 'all' from filtering)
            status = request.args.get('status')
            if status and status != 'all':
                filters['status'] = status
            
            # Enquiry type filter
            enquiry_type = request.args.get('enquiry_type')
            if enquiry_type:
                filters['enquiry_type'] = enquiry_type
            
            # User filter
            user_id = request.args.get('user_id')
            if user_id:
                user = Admin_And_User.objects(id=user_id).first()
                if user:
                    filters['user'] = user
            
            # Land filter
            land_id = request.args.get('land_id')
            if land_id:
                land = Land.objects(id=land_id).first()
                if land:
                    filters['land'] = land
            
            # Date range filter
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            if start_date:
                filters['created_at__gte'] = datetime.fromisoformat(start_date)
            if end_date:
                filters['created_at__lte'] = datetime.fromisoformat(end_date)
            
            # Follow-up filter
            is_followed_up = request.args.get('is_followed_up')
            if is_followed_up is not None:
                filters['is_followed_up'] = is_followed_up.lower() == 'true'
            
            # Get enquiries with filters
            enquiries = Enquiry.objects(**filters).order_by('-created_at')
            
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
    def get_pending_enquiries():
        """
        Get all pending enquiries
        GET /api/admin/enquiries/pending
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get pending enquiries
            pending = Enquiry.objects(status='pending').order_by('-created_at')
            
            return jsonify({
                "total": pending.count(),
                "enquiries": [e.to_json() for e in pending]
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_enquiry_by_id():
        """
        Get any enquiry by ID (admin can view all)
        GET /api/admin/enquiries/enquiry?id=<enquiry_id>
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            return jsonify(enquiry.to_json()), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def update_enquiry_status():
        """
        Update enquiry status
        PUT /api/admin/enquiries/update-status
        Body: { enquiry_id, status }
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            enquiry_id = data.get('enquiry_id')
            new_status = data.get('status')
            
            if not enquiry_id or not new_status:
                return jsonify({"error": "Enquiry ID and status are required"}), 400
            
            # Validate status
            valid_statuses = ['pending', 'contacted', 'in_progress', 'completed', 'cancelled']
            if new_status not in valid_statuses:
                return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Update status
            old_status = enquiry.status
            enquiry.status = new_status
            enquiry.updated_at = datetime.now(timezone.utc)
            
            # Set timestamps based on status
            if new_status == 'contacted' and not enquiry.contacted_at:
                enquiry.contacted_at = datetime.now(timezone.utc)
            elif new_status == 'completed' and not enquiry.completed_at:
                enquiry.completed_at = datetime.now(timezone.utc)
            
            enquiry.save()
            
            return jsonify({
                "message": f"Enquiry status updated from '{old_status}' to '{new_status}'",
                "enquiry": enquiry.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def add_admin_notes():
        """
        Add or update admin notes for an enquiry
        PUT /api/admin/enquiries/add-notes
        Body: { enquiry_id, admin_notes }
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            enquiry_id = data.get('enquiry_id')
            admin_notes = data.get('admin_notes')
            
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Update notes
            enquiry.admin_notes = admin_notes
            enquiry.updated_at = datetime.now(timezone.utc)
            enquiry.save()
            
            return jsonify({
                "message": "Admin notes updated successfully",
                "enquiry": enquiry.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def mark_followed_up():
        """
        Mark enquiry as followed up
        PUT /api/admin/enquiries/mark-followed-up
        Body: { enquiry_id, follow_up_date? }
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            enquiry_id = data.get('enquiry_id')
            
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Mark as followed up
            enquiry.is_followed_up = True
            enquiry.follow_up_date = datetime.now(timezone.utc)
            
            if data.get('follow_up_date'):
                try:
                    enquiry.follow_up_date = datetime.fromisoformat(data['follow_up_date'])
                except:
                    pass
            
            enquiry.updated_at = datetime.now(timezone.utc)
            enquiry.save()
            
            return jsonify({
                "message": "Enquiry marked as followed up",
                "enquiry": enquiry.to_json()
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def update_enquiry():
        """
        Update any field of an enquiry
        PUT /api/admin/enquiries/update?id=<enquiry_id>
        Body: { contact_name?, contact_phone?, contact_email?, message?, budget?, status?, admin_notes?, etc. }
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Get update data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Update fields
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
            if 'status' in data:
                valid_statuses = ['pending', 'contacted', 'in_progress', 'completed', 'cancelled']
                if data['status'] in valid_statuses:
                    enquiry.status = data['status']
            if 'admin_notes' in data:
                enquiry.admin_notes = data['admin_notes']
            if 'is_followed_up' in data:
                enquiry.is_followed_up = data['is_followed_up']
            
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
    def delete_enquiry():
        """
        Delete any enquiry
        DELETE /api/admin/enquiries/delete?id=<enquiry_id>
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get enquiry ID
            enquiry_id = request.args.get('id')
            if not enquiry_id:
                return jsonify({"error": "Enquiry ID is required"}), 400
            
            # Get enquiry
            enquiry = Enquiry.objects(id=enquiry_id).first()
            if not enquiry:
                return jsonify({"error": "Enquiry not found"}), 404
            
            # Store info before deletion
            enquiry_info = {
                "id": str(enquiry.id),
                "contact_name": enquiry.contact_name,
                "enquiry_type": enquiry.enquiry_type
            }
            
            # Delete enquiry
            enquiry.delete()
            
            return jsonify({
                "message": "Enquiry deleted successfully",
                "deleted_enquiry": enquiry_info
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get dashboard statistics for enquiries
        GET /api/admin/enquiries/dashboard-stats
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get counts
            total_enquiries = Enquiry.objects.count()
            pending_enquiries = Enquiry.objects(status='pending').count()
            contacted_enquiries = Enquiry.objects(status='contacted').count()
            in_progress_enquiries = Enquiry.objects(status='in_progress').count()
            completed_enquiries = Enquiry.objects(status='completed').count()
            cancelled_enquiries = Enquiry.objects(status='cancelled').count()
            
            # Get counts by enquiry type
            enquiry_type_stats = {}
            for enq_type in ['buy_interest', 'site_visit', 'price_negotiation', 'general_enquiry']:
                enquiry_type_stats[enq_type] = Enquiry.objects(enquiry_type=enq_type).count()
            
            # Follow-up stats
            followed_up = Enquiry.objects(is_followed_up=True).count()
            not_followed_up = Enquiry.objects(is_followed_up=False).count()
            
            # Get recent enquiries
            recent_enquiries = Enquiry.objects().order_by('-created_at').limit(10)
            recent_pending = Enquiry.objects(status='pending').order_by('-created_at').limit(5)
            
            # Get most enquired lands
            from collections import Counter
            land_ids = [str(e.land.id) for e in Enquiry.objects() if e.land]
            most_enquired = Counter(land_ids).most_common(5)
            
            stats = {
                "overview": {
                    "total_enquiries": total_enquiries,
                    "pending_enquiries": pending_enquiries,
                    "contacted_enquiries": contacted_enquiries,
                    "in_progress_enquiries": in_progress_enquiries,
                    "completed_enquiries": completed_enquiries,
                    "cancelled_enquiries": cancelled_enquiries
                },
                "by_enquiry_type": enquiry_type_stats,
                "follow_up_stats": {
                    "followed_up": followed_up,
                    "not_followed_up": not_followed_up
                },
                "recent_enquiries": [e.to_json() for e in recent_enquiries],
                "pending_enquiries": [e.to_json() for e in recent_pending],
                "most_enquired_lands": [{"land_id": land_id, "count": count} for land_id, count in most_enquired]
            }
            
            return jsonify(stats), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def bulk_update_status():
        """
        Update status of multiple enquiries at once
        POST /api/admin/enquiries/bulk-update-status
        Body: { enquiry_ids: [id1, id2, ...], status }
        """
        try:
            # Verify admin
            payload, error = EnquiryAdminController.verify_admin()
            if error:
                return error
            
            # Get data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            enquiry_ids = data.get('enquiry_ids', [])
            new_status = data.get('status')
            
            if not enquiry_ids or not new_status:
                return jsonify({"error": "Enquiry IDs and status are required"}), 400
            
            # Validate status
            valid_statuses = ['pending', 'contacted', 'in_progress', 'completed', 'cancelled']
            if new_status not in valid_statuses:
                return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
            
            # Update all enquiries
            updated_count = 0
            failed = []
            
            for enquiry_id in enquiry_ids:
                try:
                    enquiry = Enquiry.objects(id=enquiry_id).first()
                    if enquiry:
                        enquiry.status = new_status
                        enquiry.updated_at = datetime.now(timezone.utc)
                        
                        if new_status == 'contacted' and not enquiry.contacted_at:
                            enquiry.contacted_at = datetime.now(timezone.utc)
                        elif new_status == 'completed' and not enquiry.completed_at:
                            enquiry.completed_at = datetime.now(timezone.utc)
                        
                        enquiry.save()
                        updated_count += 1
                    else:
                        failed.append({"id": enquiry_id, "reason": "Not found"})
                except Exception as e:
                    failed.append({"id": enquiry_id, "reason": str(e)})
            
            return jsonify({
                "message": "Bulk status update completed",
                "updated": updated_count,
                "failed": len(failed),
                "failed_details": failed
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
