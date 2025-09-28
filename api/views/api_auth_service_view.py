
import os
from decouple import config  # Ensure this is at the top
import requests
import logging
import json
from urllib.parse import urljoin
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import jwt
from functools import wraps
logger = logging.getLogger(__name__)
SECRET_KEY = settings.SECRET_KEY  # Ensure to use the project's secret key

def get_internal_jwt_token():
    """  Securely fetches a JWT token for `api_service_user` using internal credentials without exposing them to the frontend. """
    api_url = urljoin(settings.BASE_BACKEND_URL, "api/token/")
    payload = {
        "username": settings.API_SERVICE_USERNAME,
        "password": settings.API_SERVICE_PASSWORD,
    }

    # Determine SSL certificate verification logic
    # Load cert path only for dev/IP
    ENV = settings.ENVIRONMENT
    DEFAULT_CA_PATH = os.path.expanduser(config("SSL_CA_BUNDLE", default="~/Library/Application Support/mkcert/rootCA.pem"))

    # Use cert path only in local/IP — for ngrok or domain, use system trust
    if ENV in ["local", "ip"]:
        verify_ssl = DEFAULT_CA_PATH if os.path.exists(DEFAULT_CA_PATH) else False
    else:
        verify_ssl = True

    try:
        logger.info(f" [AUTH] Requesting JWT Token from {api_url}")
        logger.info(f" SSL Verification Mode: {verify_ssl}")

        response = requests.post(api_url, json=payload, timeout=5, verify=verify_ssl)

        logger.info(f" [AUTH] Backend Response Code: {response.status_code}")
        logger.info(f" [AUTH] Backend Response: {response.text}")

        if response.status_code == 200:
            return response.json().get("access")
        return None

    except requests.RequestException as e:
        logger.error(f" [AUTH] Exception while fetching token: {str(e)}")
        return None
    
def extract_token_from_request(request):
    """  Extracts the JWT token from either:
       - The HttpOnly Cookie (Preferred)
       - The Authorization Header (Fallback)
    """
    logger.info(" [AUTH] Attempting to extract token from request...")
    #  Check for token in HttpOnly Cookie
    token = request.COOKIES.get("access_token")
    if token:
        logger.info(" [AUTH] Token retrieved from cookies: %s", token[:30] + "...(truncated)")  # Truncate for security
        return token
    #  Fallback to Authorization Header if no cookie is found
    logger.warning(" [AUTH] No token found in cookies. Checking Authorization header...")
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.info(" [AUTH] Token retrieved from Authorization header: %s", token[:30] + "...(truncated)")
        return token
    logger.error(" [AUTH] No token found in request (neither in cookies nor headers)")
    return None
    # Fetch domain from env file

def set_auth_cookie(response, token):
    """  Securely store the JWT token in an HttpOnly cookie. Reads configuration dynamically from `.env` file. """
    logger.info(" [AUTH] Setting JWT token in HttpOnly cookie...")
    #  Fetch cookie-related settings from environment variables
    #  Load Cookie Configuration from .env
    COOKIE_DOMAIN = config("COOKIE_DOMAIN", default="localhost")
    COOKIE_SECURE = config("COOKIE_SECURE", default=False, cast=bool)
    COOKIE_SAMESITE = config("COOKIE_SAMESITE", default="None")
    COOKIE_PATH = config("COOKIE_PATH", default="/")
    #  Set the authentication cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,   #  Protects against XSS attacks
        secure=settings.COOKIE_SECURE,        #  from settings.py
        samesite=settings.COOKIE_SAMESITE,    #  from settings.py
        domain=settings.COOKIE_DOMAIN,        #  dynamically resolved IP/local/prod
        path=settings.COOKIE_PATH,            #  from settings.py
    )
    logger.info(f" [AUTH] JWT token stored in HttpOnly cookie. Domain: {COOKIE_DOMAIN}, Secure: {COOKIE_SECURE}, SameSite: {COOKIE_SAMESITE}")
    return response

def require_authentication(view_func):
    """  Decorator to check for access_token in HttpOnly Cookie """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = extract_token_from_request(request)
        if not token:
            logger.error(" [AUTH] Unauthorized: Token missing")
            return JsonResponse({"error": "Unauthorized: Token missing"}, status=401)
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded  #  Attach user info to request
        except jwt.ExpiredSignatureError:
            logger.error(" [AUTH] Unauthorized: Token expired")
            return JsonResponse({"error": "Unauthorized: Token expired"}, status=401)
        except jwt.InvalidTokenError:
            logger.error(" [AUTH] Unauthorized: Invalid token")
            return JsonResponse({"error": "Unauthorized: Invalid token"}, status=401)
        return view_func(request, *args, **kwargs)
    
    return wrapper

@require_GET
@csrf_exempt
def internal_token_view(request):
    """
     Secure API Endpoint to fetch an internal service token.
    Returns the JWT as JSON.
    """
    token = get_internal_jwt_token()
    if token:
        return JsonResponse({"access_token": token}, content_type="application/json")
    else:
        logger.error(" [AUTH] Could not retrieve service token")
        return JsonResponse({"error": "Could not retrieve service token"}, status=500, content_type="application/json")

@require_GET
@csrf_exempt
def get_service_token(request):
    """
     Provides a JWT service token to the frontend,
    securely stored in an **HTTP-Only Cookie**.
    """
    token = get_internal_jwt_token()
        #  Detect if running locally or on subdomain
    if "localhost" not in request.get_host():
        #cookie_domain = ".camelfoundation.org"  # Use subdomain in production
        cookie_domain = "cftdomaap-dev.camelfoundation.org"  # Use subdomain in production
    if token:
        response = JsonResponse({"message": "Token stored securely!!"}, content_type="application/json")
        logger.info(f" [AUTH] JWT token stored in HttpOnly cookie : {response}")
        print("Token - PRINT:", token)
        return set_auth_cookie(response, token)  #  Store token in HttpOnly cookie
    else:
        logger.error(" [AUTH] Could not retrieve service token")
        return JsonResponse({"error": "Could not retrieve service token"}, status=500, content_type="application/json")

@require_GET
@csrf_exempt
def refresh_service_token(request):
    """
     Refresh the JWT access token by issuing a new one.
    """
    token = get_internal_jwt_token()
        #  Set cookie domain for subdomains
    #cookie_domain = ".camelfoundation.org"  # Allows access across subdomains
    cookie_domain = "cftdomaap-dev.camelfoundation.org"  # Use subdomain in production
    if token:
        response = JsonResponse({"message": "Token refreshed!"}, content_type="application/json")
        return set_auth_cookie(response, token)  #  Securely update token
    else:
        logger.error(" [AUTH] Failed to refresh service token")
        return JsonResponse({"error": "Could not refresh service token"}, status=500, content_type="application/json")

@require_GET
@csrf_exempt
def logout(request):
    """
     Securely clears the access token by deleting the cookie.
    """
    response = JsonResponse({"message": "Logged out successfully!"}, content_type="application/json")
    response.delete_cookie("access_token")
    logger.info(" [AUTH] User logged out. Access token deleted.")
    return response

@require_GET
@csrf_exempt
def debug_token_view(request):
    """
     Debugging Endpoint: Logs whether Django can read cookies properly.
    """
    logger.info(" [DEBUG] Checking request cookies...")
    cookies_received = request.COOKIES  # Log all cookies
    logger.info(" [DEBUG] Cookies received: %s", cookies_received)
    token = extract_token_from_request(request)
    if token:
        return JsonResponse({"message": " Token retrieved successfully!", "token": token[:30] + "...(truncated)"})
    else:
        return JsonResponse({"error": " No token found!"}, status=401)
    
def my_protected_view(request):
    """
     Debugging View to Check if Django Receives the JWT Token in Cookies.
    """
    logger.info(f" Cookies Received: {request.COOKIES}")  # Log all received cookies
    token = request.COOKIES.get("access_token")  # Try fetching the token
    print("Incoming Cookies - PRINT:", request.COOKIES)  # Debugging
    print("Authorization Header - PRINT:", request.headers.get("Authorization"))  # Debugging
    if token:
        logger.info(f" Token Found: {token[:30]}... (Truncated)")  # Log only first 30 chars
        return JsonResponse({"message": " Token detected!", "token": token[:30] + "...(truncated)"})
    else:
        logger.warning(" No Token Found in Cookies")
        return JsonResponse({"error": " No token found in cookies!"}, status=401)    
