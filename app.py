from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from mongoengine import connect,get_connection
from Routes.landRoutes import land_bp
from Routes.userRoutes import user_bp
from Routes.userRoutes import admin_bp
from Routes.loginRoutes import login_bp
from Routes.sellLandUserRoutes import sell_land_user_bp
from Routes.sellLandAdminRoutes import sell_land_admin_bp
from Routes.enquiryUserRoutes import enquiry_user_bp
from Routes.enquiryAdminRoutes import enquiry_admin_bp
from Routes.landAdminRoutes import land_admin_bp
from Routes.imageUploadRoutes import image_upload_bp
from flask_cors import CORS
from Utils.CheckAuthorization import CheckAuthorization


load_dotenv()

app = Flask(__name__)
CORS(app)
print(os.getenv("DB_CONNECT_STRING"))

# Check if using MongoDB Atlas (cloud) or local MongoDB
db_connect_string = os.getenv("DB_CONNECT_STRING")
if db_connect_string and "mongodb+srv" in db_connect_string:
    # MongoDB Atlas - use SSL
    connect(db=os.getenv("DB"), host=db_connect_string, ssl=True)
else:
    # Local MongoDB - no SSL
    connect(db=os.getenv("DB", "gem_db"), host="mongodb://localhost:27017/")

client = get_connection()

@app.before_request
def check_auth_token():
    if request.method == 'OPTIONS':
        return
    
    # Routes that don't require authentication (exact matches)
    except_routes = [
        '/api/login/login',  # Login endpoint
        '/api/user/create',  # User registration
        '/api/user/enquiries/available-lands',  # Public land browsing
        '/api/user/enquiries/guest-enquiry',  # Guest enquiry submission
        '/api/user/enquiries/land',  # Land details via query param (?id=)
        '/health'  # Health check
    ]

    # Route prefixes that are public (e.g., /api/user/enquiries/land/<id>)
    except_prefixes = [
        '/api/user/enquiries/land'
    ]

    # Check if current path matches any except route or prefix
    current_path = request.path
    if current_path not in except_routes and not any(current_path.startswith(p) for p in except_prefixes):
        token = request.headers.get("token")  # Changed from "Authorization" to "token"
        if not token:
            return jsonify({"error": "Token required"}), 401
        
        verify = CheckAuthorization.VerifyToken(token)
        if verify != True:
            return verify

@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.server_info()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({"status": "healthy", "database": db_status}), 200 if db_status == "connected" else 500

# Register blueprints
app.register_blueprint(land_bp, url_prefix='/api/land')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(login_bp, url_prefix='/api/login')
app.register_blueprint(sell_land_user_bp)  # Already has url_prefix in blueprint
app.register_blueprint(sell_land_admin_bp)  # Already has url_prefix in blueprint
app.register_blueprint(enquiry_user_bp)  # Already has url_prefix in blueprint
app.register_blueprint(enquiry_admin_bp)  # Already has url_prefix in blueprint
app.register_blueprint(land_admin_bp, url_prefix='/api/admin/lands')
app.register_blueprint(image_upload_bp)  # Already has url_prefix in blueprint

if __name__ == '__main__':
        app.run(debug=True)

