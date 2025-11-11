from flask import Blueprint
from Controllers.sellLandAdminController import SellLandAdminController

# Create blueprint for admin sell land routes
sell_land_admin_bp = Blueprint('sell_land_admin', __name__, url_prefix='/api/admin/sell-land')

@sell_land_admin_bp.route('/all', methods=['GET'])
def get_all_submissions():
    """
    GET /api/admin/sell-land/all
    Get all sell land submissions with optional filters
    Requires: token in headers (admin role)
    Query params: status?, land_type?, user_id?, start_date?, end_date?
    """
    return SellLandAdminController.get_all_submissions()

@sell_land_admin_bp.route('/pending', methods=['GET'])
def get_pending_submissions():
    """
    GET /api/admin/sell-land/pending
    Get all pending submissions
    Requires: token in headers (admin role)
    """
    return SellLandAdminController.get_pending_submissions()

@sell_land_admin_bp.route('/submission', methods=['GET'])
def get_submission_by_id():
    """
    GET /api/admin/sell-land/submission?id=<submission_id>
    Get any submission by ID
    Requires: token in headers (admin role)
    Query params: id
    """
    return SellLandAdminController.get_submission_by_id()

@sell_land_admin_bp.route('/approve', methods=['POST'])
def approve_submission():
    """
    POST /api/admin/sell-land/approve
    Approve a submission
    Requires: token in headers (admin role)
    Body: { submission_id }
    """
    return SellLandAdminController.approve_submission()

@sell_land_admin_bp.route('/reject', methods=['POST'])
def reject_submission():
    """
    POST /api/admin/sell-land/reject
    Reject a submission
    Requires: token in headers (admin role)
    Body: { submission_id, reason? }
    """
    return SellLandAdminController.reject_submission()

@sell_land_admin_bp.route('/move-to-land', methods=['POST'])
def move_to_land():
    """
    POST /api/admin/sell-land/move-to-land
    Move approved submission to Land model
    Requires: token in headers (admin role)
    Body: { submission_id, title?, description?, images_urls? }
    """
    return SellLandAdminController.move_to_land()

@sell_land_admin_bp.route('/update', methods=['PUT'])
def update_submission():
    """
    PUT /api/admin/sell-land/update?id=<submission_id>
    Update any submission field
    Requires: token in headers (admin role)
    Query params: id
    Body: { owner_name?, contact_phone?, location?, price?, area?, land_type?, status?, description? }
    """
    return SellLandAdminController.update_submission()

@sell_land_admin_bp.route('/delete', methods=['DELETE'])
def delete_submission():
    """
    DELETE /api/admin/sell-land/delete?id=<submission_id>
    Delete any submission
    Requires: token in headers (admin role)
    Query params: id
    """
    return SellLandAdminController.delete_submission()

@sell_land_admin_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """
    GET /api/admin/sell-land/dashboard-stats
    Get dashboard statistics
    Requires: token in headers (admin role)
    """
    return SellLandAdminController.get_dashboard_stats()

@sell_land_admin_bp.route('/bulk-approve', methods=['POST'])
def bulk_approve():
    """
    POST /api/admin/sell-land/bulk-approve
    Approve multiple submissions at once
    Requires: token in headers (admin role)
    Body: { submission_ids: [id1, id2, ...] }
    """
    return SellLandAdminController.bulk_approve()

@sell_land_admin_bp.route('/bulk-delete', methods=['POST'])
def bulk_delete():
    """
    POST /api/admin/sell-land/bulk-delete
    Delete multiple submissions at once
    Requires: token in headers (admin role)
    Body: { submission_ids: [id1, id2, ...] }
    """
    return SellLandAdminController.bulk_delete()
