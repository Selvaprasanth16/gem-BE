from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from mongoengine import connect,get_connection
from Routes.landRoutes import land_bp
from Routes.userRoutes import user_bp
from Routes.userRoutes import admin_bp
from Routes.loginRoutes import login_bp
from flask_cors import CORS
from Utils.CheckAuthorization import CheckAuthorization


load_dotenv()

app = Flask(__name__)
CORS(app)
print(os.getenv("DB_CONNECT_STRING"))
connect(db=os.getenv("DB"), host=os.getenv("DB_CONNECT_STRING"), ssl=True)

client = get_connection()

@app.before_request
def check_auth_token():
    if request.method == 'OPTIONS':
        return
    
    # Routes that don't require authentication
    except_routes = [
        '/api/login/login',  # Login endpoint
        '/api/user/create',  # User registration
        '/health'  # Health check
    ]

    if request.path not in except_routes:
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

if __name__ == '__main__':
        app.run(debug=True)

