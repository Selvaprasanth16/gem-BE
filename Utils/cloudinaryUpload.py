import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

class CloudinaryUpload:
    """
    Utility class for uploading and managing images on Cloudinary
    """
    
    @staticmethod
    def upload_image(file, folder="gem_lands"):
        """
        Upload an image to Cloudinary
        
        Args:
            file: File object from Flask request
            folder: Cloudinary folder name (default: "gem_lands")
            
        Returns:
            dict: Contains 'url' and 'public_id' of uploaded image
        """
        try:
            # Upload image to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type="image",
                allowed_formats=["jpg", "jpeg", "png", "webp", "gif"],
                transformation=[
                    {'width': 1200, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
            
            return {
                'url': result.get('secure_url'),
                'public_id': result.get('public_id'),
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format')
            }
        except Exception as e:
            raise Exception(f"Failed to upload image: {str(e)}")
    
    @staticmethod
    def upload_multiple_images(files, folder="gem_lands"):
        """
        Upload multiple images to Cloudinary
        
        Args:
            files: List of file objects from Flask request
            folder: Cloudinary folder name
            
        Returns:
            list: List of dicts containing image URLs and public_ids
        """
        try:
            uploaded_images = []
            
            for file in files:
                result = CloudinaryUpload.upload_image(file, folder)
                uploaded_images.append(result)
            
            return uploaded_images
        except Exception as e:
            raise Exception(f"Failed to upload images: {str(e)}")
    
    @staticmethod
    def delete_image(public_id):
        """
        Delete an image from Cloudinary
        
        Args:
            public_id: Public ID of the image to delete
            
        Returns:
            dict: Deletion result
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result
        except Exception as e:
            raise Exception(f"Failed to delete image: {str(e)}")
    
    @staticmethod
    def delete_multiple_images(public_ids):
        """
        Delete multiple images from Cloudinary
        
        Args:
            public_ids: List of public IDs to delete
            
        Returns:
            dict: Deletion results
        """
        try:
            results = []
            for public_id in public_ids:
                result = CloudinaryUpload.delete_image(public_id)
                results.append(result)
            return results
        except Exception as e:
            raise Exception(f"Failed to delete images: {str(e)}")
    
    @staticmethod
    def extract_public_id_from_url(url):
        """
        Extract public_id from Cloudinary URL
        
        Args:
            url: Cloudinary image URL
            
        Returns:
            str: Public ID
        """
        try:
            # Extract public_id from URL
            # Example: https://res.cloudinary.com/cloud_name/image/upload/v123456/folder/image.jpg
            # Public ID: folder/image
            parts = url.split('/')
            # Find the index of 'upload'
            upload_index = parts.index('upload')
            # Get everything after version number
            public_id_parts = parts[upload_index + 2:]  # Skip version
            # Join and remove extension
            public_id = '/'.join(public_id_parts).rsplit('.', 1)[0]
            return public_id
        except Exception as e:
            raise Exception(f"Failed to extract public_id: {str(e)}")
