from flask import Blueprint
from Controllers.siteContentController import SiteContentController

site_content_bp = Blueprint('site_content', __name__)

# Public landing content
site_content_bp.add_url_rule('/public/landing', view_func=SiteContentController.get_public_landing, methods=['GET'])

# Admin landing content
site_content_bp.add_url_rule('/admin/landing', view_func=SiteContentController.get_admin_landing, methods=['GET'])
site_content_bp.add_url_rule('/admin/landing', view_func=SiteContentController.update_landing, methods=['PUT'])
