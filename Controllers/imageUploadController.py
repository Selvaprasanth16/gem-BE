from flask import request, jsonify
from Utils.cloudinaryUpload import CloudinaryUpload
from Utils.CheckAuthorization import CheckAuthorization
import jwt
import os


class ImageUploadController:
    """
    Controller for handling image uploads to Cloudinary
    """
    
    @staticmethod
    def upload_land_images():
        """
        Upload multiple land images to Cloudinary
        POST /api/admin/images/upload-land-images
        Requires: Admin authentication
        Body: multipart/form-data with 'images' field containing files
        """
        try:
            # Check admin authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token and check role
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            
            # Check if files are present
            if 'images' not in request.files:
                return jsonify({"error": "No images provided"}), 400
            
            files = request.files.getlist('images')
            
            if not files or len(files) == 0:
                return jsonify({"error": "No images provided"}), 400
            
            # Validate file count (max 10 images)
            if len(files) > 10:
                return jsonify({"error": "Maximum 10 images allowed"}), 400
            
            # Validate file types
            allowed_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
            for file in files:
                if file.filename == '':
                    return jsonify({"error": "Empty filename"}), 400
                
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext not in allowed_extensions:
                    return jsonify({"error": f"Invalid file type: {file.filename}. Allowed: {', '.join(allowed_extensions)}"}), 400
            
            # Upload images to Cloudinary
            uploaded_images = CloudinaryUpload.upload_multiple_images(files, folder="gem_lands")
            
            # Extract URLs
            image_urls = [img['url'] for img in uploaded_images]
            
            return jsonify({
                "message": "Images uploaded successfully",
                "images": uploaded_images,
                "image_urls": image_urls,
                "count": len(image_urls)
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def delete_land_image():
        """
        Delete a land image from Cloudinary
        DELETE /api/admin/images/delete-land-image
        Requires: Admin authentication
        Body: { "image_url": "cloudinary_url" } or { "public_id": "cloudinary_public_id" }
        """
        try:
            # Check admin authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token and check role
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Get public_id or extract from URL
            public_id = data.get('public_id')
            image_url = data.get('image_url')
            
            if not public_id and not image_url:
                return jsonify({"error": "Either public_id or image_url is required"}), 400
            
            # Extract public_id from URL if not provided
            if not public_id and image_url:
                public_id = CloudinaryUpload.extract_public_id_from_url(image_url)
            
            # Delete image from Cloudinary
            result = CloudinaryUpload.delete_image(public_id)
            
            return jsonify({
                "message": "Image deleted successfully",
                "result": result
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @staticmethod
    def delete_multiple_land_images():
        """
        Delete multiple land images from Cloudinary
        DELETE /api/admin/images/delete-multiple-land-images
        Requires: Admin authentication
        Body: { "image_urls": ["url1", "url2"] } or { "public_ids": ["id1", "id2"] }
        """
        try:
            # Check admin authentication
            token = request.headers.get('token')
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            verify = CheckAuthorization.VerifyToken(token)
            if verify != True:
                return verify
            
            # Decode token and check role
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Get public_ids or extract from URLs
            public_ids = data.get('public_ids', [])
            image_urls = data.get('image_urls', [])
            
            if not public_ids and not image_urls:
                return jsonify({"error": "Either public_ids or image_urls is required"}), 400
            
            # Extract public_ids from URLs if not provided
            if not public_ids and image_urls:
                public_ids = [CloudinaryUpload.extract_public_id_from_url(url) for url in image_urls]
            
            # Delete images from Cloudinary
            results = CloudinaryUpload.delete_multiple_images(public_ids)
            
            return jsonify({
                "message": "Images deleted successfully",
                "results": results,
                "count": len(results)
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
