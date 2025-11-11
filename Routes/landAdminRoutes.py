from flask import Blueprint
from Controllers.landAdminController import LandAdminController

land_admin_bp = Blueprint('land_admin', __name__)

# Create new land
land_admin_bp.add_url_rule('/create', view_func=LandAdminController.create_land, methods=['POST'])

# Get all lands with filters
land_admin_bp.add_url_rule('/all', view_func=LandAdminController.get_all_lands, methods=['GET'])

# Update land status
land_admin_bp.add_url_rule('/update-status', view_func=LandAdminController.update_land_status, methods=['PUT'])

# Update land details
land_admin_bp.add_url_rule('/update', view_func=LandAdminController.update_land, methods=['PUT'])

# Delete land
land_admin_bp.add_url_rule('/delete', view_func=LandAdminController.delete_land, methods=['DELETE'])

# Get dashboard statistics
land_admin_bp.add_url_rule('/dashboard-stats', view_func=LandAdminController.get_dashboard_stats, methods=['GET'])
