from flask import Blueprint, request
from Controllers.enquiryUserController import EnquiryUserController

# Create blueprint for user enquiry routes
enquiry_user_bp = Blueprint('enquiry_user', __name__, url_prefix='/api/user/enquiries')

@enquiry_user_bp.route('/create', methods=['POST'])
def create_enquiry():
    """
    POST /api/user/enquiries/create
    Create a new enquiry for a land listing
    Requires: token in headers
    Body: { land_id, enquiry_type, contact_name, contact_phone, contact_email, message?, budget?, preferred_contact_time? }
    """
    return EnquiryUserController.create_enquiry()

@enquiry_user_bp.route('/my-enquiries', methods=['GET'])
def get_my_enquiries():
    """
    GET /api/user/enquiries/my-enquiries
    Get all enquiries created by authenticated user
    Requires: token in headers
    """
    return EnquiryUserController.get_my_enquiries()

@enquiry_user_bp.route('/enquiry', methods=['GET'])
def get_enquiry_by_id():
    """
    GET /api/user/enquiries/enquiry?id=<enquiry_id>
    Get a specific enquiry by ID (user's own)
    Requires: token in headers
    Query params: id
    """
    return EnquiryUserController.get_enquiry_by_id()

@enquiry_user_bp.route('/update', methods=['PUT'])
def update_enquiry():
    """
    PUT /api/user/enquiries/update?id=<enquiry_id>
    Update user's own pending enquiry
    Requires: token in headers
    Query params: id
    Body: { contact_name?, contact_phone?, contact_email?, message?, budget?, preferred_contact_time? }
    """
    return EnquiryUserController.update_enquiry()

@enquiry_user_bp.route('/cancel', methods=['PUT'])
def cancel_enquiry():
    """
    PUT /api/user/enquiries/cancel?id=<enquiry_id>
    Cancel user's own enquiry
    Requires: token in headers
    Query params: id
    """
    return EnquiryUserController.cancel_enquiry()

@enquiry_user_bp.route('/guest-enquiry', methods=['POST'])
def create_guest_enquiry():
    """
    POST /api/user/enquiries/guest-enquiry
    Create a guest enquiry (no authentication required)
    Body: { land_id, contact_phone }
    """
    return EnquiryUserController.create_guest_enquiry()

@enquiry_user_bp.route('/available-lands', methods=['GET'])
def get_available_lands():
    """
    GET /api/user/enquiries/available-lands
    Get all available lands for browsing
    Query params: property_type?, location?, min_price?, max_price?, min_size?, max_size?
    """
    return EnquiryUserController.get_available_lands()

# New: Get single land by ID - supports both query param and path param styles
@enquiry_user_bp.route('/land', methods=['GET'])
def get_land_query():
    """
    GET /api/user/enquiries/land?id=<land_id>
    Fetch land by ID using query parameter.
    """
    land_id = request.args.get('id')
    return EnquiryUserController.get_land_by_id(land_id)

@enquiry_user_bp.route('/land/<land_id>', methods=['GET'])
def get_land_path(land_id):
    """
    GET /api/user/enquiries/land/<land_id>
    Fetch land by ID using path parameter.
    """
    return EnquiryUserController.get_land_by_id(land_id)
