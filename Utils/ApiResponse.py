from flask import jsonify

class ApiResponse:
    """
    Standardized API response format for consistency across all endpoints
    """
    
    @staticmethod
    def success(data=None, message=None, status_code=200):
        """
        Return a successful response
        
        Args:
            data: The data to return (dict, list, or any JSON-serializable object)
            message: Optional success message
            status_code: HTTP status code (default: 200)
        
        Returns:
            Flask JSON response with standardized format
        """
        response = {
            "success": True,
            "data": data if data is not None else {}
        }
        
        if message:
            response["message"] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message, status_code=400, errors=None):
        """
        Return an error response
        
        Args:
            message: Error message
            status_code: HTTP status code (default: 400)
            errors: Optional detailed error information
        
        Returns:
            Flask JSON response with standardized format
        """
        response = {
            "success": False,
            "error": message
        }
        
        if errors:
            response["errors"] = errors
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(data, message="Resource created successfully"):
        """
        Return a created response (201)
        
        Args:
            data: The created resource data
            message: Success message
        
        Returns:
            Flask JSON response with 201 status
        """
        return ApiResponse.success(data, message, 201)
    
    @staticmethod
    def updated(data, message="Resource updated successfully"):
        """
        Return an updated response (200)
        
        Args:
            data: The updated resource data
            message: Success message
        
        Returns:
            Flask JSON response with 200 status
        """
        return ApiResponse.success(data, message, 200)
    
    @staticmethod
    def deleted(message="Resource deleted successfully"):
        """
        Return a deleted response (200)
        
        Args:
            message: Success message
        
        Returns:
            Flask JSON response with 200 status
        """
        return ApiResponse.success({}, message, 200)
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        """
        Return an unauthorized response (401)
        
        Args:
            message: Error message
        
        Returns:
            Flask JSON response with 401 status
        """
        return ApiResponse.error(message, 401)
    
    @staticmethod
    def forbidden(message="Access denied"):
        """
        Return a forbidden response (403)
        
        Args:
            message: Error message
        
        Returns:
            Flask JSON response with 403 status
        """
        return ApiResponse.error(message, 403)
    
    @staticmethod
    def not_found(message="Resource not found"):
        """
        Return a not found response (404)
        
        Args:
            message: Error message
        
        Returns:
            Flask JSON response with 404 status
        """
        return ApiResponse.error(message, 404)
    
    @staticmethod
    def validation_error(message, errors=None):
        """
        Return a validation error response (422)
        
        Args:
            message: Error message
            errors: Detailed validation errors
        
        Returns:
            Flask JSON response with 422 status
        """
        return ApiResponse.error(message, 422, errors)
    
    @staticmethod
    def server_error(message="Internal server error"):
        """
        Return a server error response (500)
        
        Args:
            message: Error message
        
        Returns:
            Flask JSON response with 500 status
        """
        return ApiResponse.error(message, 500)
