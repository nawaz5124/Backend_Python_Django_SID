
import logging
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from functools import wraps

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(BaseAuthentication):
    """
    Custom authentication class to support both:
     Header-based JWT authentication (Authorization: Bearer <token>)
     Cookie-based JWT authentication (access_token)
    """

    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        token = None

        # 1. Extract JWT from Authorization Header
        header_token = request.headers.get("Authorization")
        if header_token and header_token.startswith("Bearer "):
            token = header_token.split("Bearer ")[1]
            logger.info(f"[jwt_custom_authentication View] - Using Authorization Header Token: {token}")

        # 2. If No Header Token, Extract JWT from Cookies
        if not token:
            token = request.COOKIES.get("access_token")
            logger.info(f"[jwt_custom_authentication View] Using Access Token from Cookies: {token}")

        #  3. If No Token Found, Reject Request
        if not token:
            logger.error("[jwt_custom_authentication View] No access token found in headers or cookies")
            return None  # Allow request to continue to DRF's default 401 response

        #  4. Validate the JWT Token
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            logger.info(f"[jwt_custom_authentication View] User authenticated: {user}")
            return (user, validated_token)
        except AuthenticationFailed as e:
            logger.error(f"[jwt_custom_authentication View] Authentication failed: {str(e)}")
            return None

        return None


# Use this decorator for Function-Based Views (FBVs)
def jwt_required(view_func):
    """
    Custom decorator to handle JWT authentication for function-based views (FBVs).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth = CustomJWTAuthentication()
        user_auth_tuple = auth.authenticate(request)

        if not user_auth_tuple:
            return JsonResponse({"error": "Authentication credentials were not provided."}, status=401)

        request.user, _ = user_auth_tuple  # Set authenticated user
        return view_func(request, *args, **kwargs)

    return wrapper