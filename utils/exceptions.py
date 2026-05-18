"""
Custom exception classes for the placement portal API.
Provides standardized error handling with consistent HTTP status codes and response formats.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class APIExceptionBase(APIException):
    """Base exception class for all API exceptions with standardized format."""
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred"
    default_code = "error"
    
    def __init__(self, detail=None, code=None, data=None):
        """
        Initialize the exception with detail, code, and additional data.
        
        Args:
            detail (str): Human-readable error message
            code (str): Machine-readable error code
            data (dict): Additional context information
        """
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
        
        if code is not None:
            self.code = code
        else:
            self.code = self.default_code
        
        self.data = data or {}
        
        # Call parent init
        super().__init__(detail=self.detail, code=self.code)


class ValidationError(APIExceptionBase):
    """
    Exception for data validation errors.
    Status code: 400 Bad Request
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error"
    default_code = "validation_error"
    
    def __init__(self, detail=None, code=None, data=None):
        if code is None:
            code = "validation_error"
        if detail is None:
            detail = "The provided data is invalid"
        super().__init__(detail=detail, code=code, data=data)


class PermissionError(APIExceptionBase):
    """
    Exception for permission/access denied errors.
    Status code: 403 Forbidden
    """
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied"
    default_code = "permission_denied"
    
    def __init__(self, detail=None, code=None, data=None):
        if code is None:
            code = "permission_denied"
        if detail is None:
            detail = "You do not have permission to perform this action"
        super().__init__(detail=detail, code=code, data=data)


class NotFoundError(APIExceptionBase):
    """
    Exception for resource not found errors.
    Status code: 404 Not Found
    """
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"
    default_code = "not_found"
    
    def __init__(self, detail=None, code=None, data=None):
        if code is None:
            code = "not_found"
        if detail is None:
            detail = "The requested resource could not be found"
        super().__init__(detail=detail, code=code, data=data)


class ConflictError(APIExceptionBase):
    """
    Exception for conflict errors (resource already exists, etc).
    Status code: 409 Conflict
    """
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict"
    default_code = "conflict"
    
    def __init__(self, detail=None, code=None, data=None):
        if code is None:
            code = "conflict"
        if detail is None:
            detail = "The request conflicts with existing data"
        super().__init__(detail=detail, code=code, data=data)


class InternalServerError(APIExceptionBase):
    """
    Exception for internal server errors.
    Status code: 500 Internal Server Error
    """
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error"
    default_code = "internal_error"
    
    def __init__(self, detail=None, code=None, data=None):
        if code is None:
            code = "internal_error"
        if detail is None:
            detail = "An internal server error occurred"
        super().__init__(detail=detail, code=code, data=data)
