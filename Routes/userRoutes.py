from Controllers.userControllers import UserController
from Controllers.adminController import AdminController
from flask import Blueprint

# Admin routes
admin_bp = Blueprint('admin', __name__)

# User management routes
admin_bp.add_url_rule('/users', view_func=AdminController.get_all_users, methods=['GET'])
admin_bp.add_url_rule('/dashboard', view_func=AdminController.get_dashboard_stats, methods=['GET'])
admin_bp.add_url_rule('/pending-lands', view_func=AdminController.get_pending_lands, methods=['GET'])
admin_bp.add_url_rule('/approve-land', view_func=AdminController.approve_land, methods=['POST'])
admin_bp.add_url_rule('/update-user', view_func=AdminController.update_user, methods=['PUT'])
admin_bp.add_url_rule('/delete-user', view_func=AdminController.delete_user, methods=['DELETE'])

# User routes
user_bp = Blueprint('user', __name__)

# User authentication and profile routes
user_bp.add_url_rule('/create', view_func=UserController.create_user, methods=['POST'])
user_bp.add_url_rule('/get', view_func=UserController.get_user, methods=['GET'])
user_bp.add_url_rule('/update', view_func=UserController.update_user, methods=['PUT'])
user_bp.add_url_rule('/delete', view_func=UserController.delete_user, methods=['DELETE'])
user_bp.add_url_rule('/my-lands', view_func=UserController.get_my_lands, methods=['GET'])
user_bp.add_url_rule('/dashboard', view_func=UserController.get_user_dashboard, methods=['GET'])
user_bp.add_url_rule('/submit-land', view_func=UserController.submit_land, methods=['POST'])
user_bp.add_url_rule('/update-land', view_func=UserController.update_my_land, methods=['PUT'])
user_bp.add_url_rule('/delete-land', view_func=UserController.delete_my_land, methods=['DELETE'])