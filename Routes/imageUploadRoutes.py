from flask import Blueprint
from Controllers.imageUploadController import ImageUploadController

# Create blueprint for image upload routes
image_upload_bp = Blueprint('image_upload', __name__, url_prefix='/api/admin/images')

@image_upload_bp.route('/upload-land-images', methods=['POST'])
def upload_land_images():
    """
    POST /api/admin/images/upload-land-images
    Upload multiple land images to Cloudinary
    Requires: Admin authentication
    Content-Type: multipart/form-data
    Body: images (file array, max 10)
    """
    return ImageUploadController.upload_land_images()

@image_upload_bp.route('/delete-land-image', methods=['DELETE'])
def delete_land_image():
    """
    DELETE /api/admin/images/delete-land-image
    Delete a single land image from Cloudinary
    Requires: Admin authentication
    Body: { "image_url": "cloudinary_url" } or { "public_id": "cloudinary_public_id" }
    """
    return ImageUploadController.delete_land_image()

@image_upload_bp.route('/delete-multiple-land-images', methods=['DELETE'])
def delete_multiple_land_images():
    """
    DELETE /api/admin/images/delete-multiple-land-images
    Delete multiple land images from Cloudinary
    Requires: Admin authentication
    Body: { "image_urls": ["url1", "url2"] } or { "public_ids": ["id1", "id2"] }
    """
    return ImageUploadController.delete_multiple_land_images()
