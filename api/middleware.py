import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings  # Fixes yellow underline

logger = logging.getLogger(__name__)

class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware to extract JWT from cookies and set it in the Authorization header.
    This allows Django’s authentication system to process the JWT even if it's stored in cookies.
    """

    def process_request(self, request):
        if settings.DEBUG:
            logger.debug(f"[Step 1]  Headers: {request.headers}")
            logger.debug(f"[Step 2]  Cookies: {request.COOKIES}")

        #  If already has Authorization header, skip
        if "Authorization" in request.headers:
            logger.info("[Step 2️] [middleware] Authorization header already present. Skipping token injection.")
            return

        #  Try JWT from cookie
        access_token = request.COOKIES.get("access_token")
        if access_token:
            masked_token = access_token[:12] + "..."  # Short log
            if settings.DEBUG:
                logger.debug(f"[Step 3️] [middleware] JWT extracted from cookies: {masked_token}")
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        else:
            logger.warning("[Step 3️] [middleware] No JWT token found in cookies.")