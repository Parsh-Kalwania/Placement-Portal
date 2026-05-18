"""
Utility functions for error handling and responses.
"""

from rest_framework.response import Response
from rest_framework import status


def error_response(error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized error response.
    
    Args:
        error_code (str): Machine-readable error code
        message (str): Human-readable error message
        details (dict): Additional error details and context
        status_code (int): HTTP status code
    
    Returns:
        Response: DRF Response object with standardized error format
    """
    error_data = {
        "error": error_code,
        "message": message,
        "details": details or {}
    }
    return Response(error_data, status=status_code)


def success_response(message=None, data=None, status_code=status.HTTP_200_OK):
    """
    Create a standardized success response.
    
    Args:
        message (str): Success message
        data (dict): Response data
        status_code (int): HTTP status code
    
    Returns:
        Response: DRF Response object with success data
    """
    response_data = {}
    
    if message:
        response_data["message"] = message
    
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)
