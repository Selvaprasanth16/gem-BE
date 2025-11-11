from flask import Blueprint
from Controllers.sellLandUserController import SellLandUserController

# Create blueprint for user sell land routes
sell_land_user_bp = Blueprint('sell_land_user', __name__, url_prefix='/api/user/sell-land')

@sell_land_user_bp.route('/create', methods=['POST'])
def create_submission():
    """
    POST /api/user/sell-land/create
    Create a new sell land form submission
    Requires: token in headers
    Body: { name, phone, location, price, area, landType, description? }
    """
    return SellLandUserController.create_submission()

@sell_land_user_bp.route('/my-submissions', methods=['GET'])
def get_my_submissions():
    """
    GET /api/user/sell-land/my-submissions
    Get all submissions created by authenticated user
    Requires: token in headers
    """
    return SellLandUserController.get_my_submissions()

@sell_land_user_bp.route('/submission', methods=['GET'])
def get_submission_by_id():
    """
    GET /api/user/sell-land/submission?id=<submission_id>
    Get a specific submission by ID (user's own)
    Requires: token in headers
    Query params: id
    """
    return SellLandUserController.get_submission_by_id()

@sell_land_user_bp.route('/update', methods=['PUT'])
def update_submission():
    """
    PUT /api/user/sell-land/update?id=<submission_id>
    Update user's own pending submission
    Requires: token in headers
    Query params: id
    Body: { name?, phone?, location?, price?, area?, description? }
    """
    return SellLandUserController.update_submission()

@sell_land_user_bp.route('/delete', methods=['DELETE'])
def delete_submission():
    """
    DELETE /api/user/sell-land/delete?id=<submission_id>
    Delete user's own submission
    Requires: token in headers
    Query params: id
    """
    return SellLandUserController.delete_submission()
