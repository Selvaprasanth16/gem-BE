from Controllers.landControllers import LandController
from flask import Blueprint

land_bp = Blueprint('land', __name__)
land_bp.add_url_rule('/create', view_func=LandController.create_land, methods=['POST'])
land_bp.add_url_rule('/get', view_func=LandController.get_land, methods=['GET'])
land_bp.add_url_rule('/update', view_func=LandController.update_land, methods=['PUT'])
land_bp.add_url_rule('/delete', view_func=LandController.delete_land, methods=['DELETE'])