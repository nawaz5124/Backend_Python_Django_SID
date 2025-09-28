from rest_framework.response import Response
from rest_framework import status

class BaseAPIException(Exception):
    """
    Base class for all API-related exceptions.
    """
    default_message = "An error occurred."
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, status_code=None):
        """
        Initialize the exception with a custom message and status code.
        """
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status_code
        super().__init__(self.message)

    def to_response(self):
        """
        Convert the exception into a DRF Response object.
        """
        return Response({"error": self.message}, status=self.status_code)


class ValidationError(BaseAPIException):
    """
    Exception for validation errors.
    """
    default_message = "Validation failed."
    default_status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(BaseAPIException):
    """
    Exception for not found errors.
    """
    default_message = "Resource not found."
    default_status_code = status.HTTP_404_NOT_FOUND


class PermissionError(BaseAPIException):
    """
    Exception for permission errors.
    """
    default_message = "Permission denied."
    default_status_code = status.HTTP_403_FORBIDDEN