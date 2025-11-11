from flask import Blueprint
from Controllers.enquiryAdminController import EnquiryAdminController

# Create blueprint for admin enquiry routes
enquiry_admin_bp = Blueprint('enquiry_admin', __name__, url_prefix='/api/admin/enquiries')

@enquiry_admin_bp.route('/all', methods=['GET'])
def get_all_enquiries():
    """
    GET /api/admin/enquiries/all
    Get all enquiries with optional filters
    Requires: token in headers (admin role)
    Query params: status?, enquiry_type?, user_id?, land_id?, start_date?, end_date?, is_followed_up?
    """
    return EnquiryAdminController.get_all_enquiries()

@enquiry_admin_bp.route('/pending', methods=['GET'])
def get_pending_enquiries():
    """
    GET /api/admin/enquiries/pending
    Get all pending enquiries
    Requires: token in headers (admin role)
    """
    return EnquiryAdminController.get_pending_enquiries()

@enquiry_admin_bp.route('/enquiry', methods=['GET'])
def get_enquiry_by_id():
    """
    GET /api/admin/enquiries/enquiry?id=<enquiry_id>
    Get any enquiry by ID
    Requires: token in headers (admin role)
    Query params: id
    """
    return EnquiryAdminController.get_enquiry_by_id()

@enquiry_admin_bp.route('/update-status', methods=['PUT'])
def update_enquiry_status():
    """
    PUT /api/admin/enquiries/update-status
    Update enquiry status
    Requires: token in headers (admin role)
    Body: { enquiry_id, status }
    """
    return EnquiryAdminController.update_enquiry_status()

@enquiry_admin_bp.route('/add-notes', methods=['PUT'])
def add_admin_notes():
    """
    PUT /api/admin/enquiries/add-notes
    Add or update admin notes for an enquiry
    Requires: token in headers (admin role)
    Body: { enquiry_id, admin_notes }
    """
    return EnquiryAdminController.add_admin_notes()

@enquiry_admin_bp.route('/mark-followed-up', methods=['PUT'])
def mark_followed_up():
    """
    PUT /api/admin/enquiries/mark-followed-up
    Mark enquiry as followed up
    Requires: token in headers (admin role)
    Body: { enquiry_id, follow_up_date? }
    """
    return EnquiryAdminController.mark_followed_up()

@enquiry_admin_bp.route('/update', methods=['PUT'])
def update_enquiry():
    """
    PUT /api/admin/enquiries/update?id=<enquiry_id>
    Update any field of an enquiry
    Requires: token in headers (admin role)
    Query params: id
    Body: { contact_name?, contact_phone?, contact_email?, message?, budget?, status?, admin_notes?, etc. }
    """
    return EnquiryAdminController.update_enquiry()

@enquiry_admin_bp.route('/delete', methods=['DELETE'])
def delete_enquiry():
    """
    DELETE /api/admin/enquiries/delete?id=<enquiry_id>
    Delete any enquiry
    Requires: token in headers (admin role)
    Query params: id
    """
    return EnquiryAdminController.delete_enquiry()

@enquiry_admin_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """
    GET /api/admin/enquiries/dashboard-stats
    Get dashboard statistics for enquiries
    Requires: token in headers (admin role)
    """
    return EnquiryAdminController.get_dashboard_stats()

@enquiry_admin_bp.route('/bulk-update-status', methods=['POST'])
def bulk_update_status():
    """
    POST /api/admin/enquiries/bulk-update-status
    Update status of multiple enquiries at once
    Requires: token in headers (admin role)
    Body: { enquiry_ids: [id1, id2, ...], status }
    """
    return EnquiryAdminController.bulk_update_status()
