from Controllers.loginController import LoginController
from flask import Blueprint

login_bp = Blueprint('login', __name__)

# Authentication routes
login_bp.add_url_rule('/login', view_func=LoginController.login, methods=['POST'])
login_bp.add_url_rule('/change-password', view_func=LoginController.change_password, methods=['POST'])
