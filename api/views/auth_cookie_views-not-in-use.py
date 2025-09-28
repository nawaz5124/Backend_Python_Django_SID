import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def determine_cookie_domain():
    """
    🔍 Determines the cookie domain using centralized environment logic.
    Driven by ACTIVE_COOKIE_DOMAIN and COOKIE_DOMAIN_MAP.
    """
    domain = settings.COOKIE_DOMAIN  # Selected via ACTIVE_COOKIE_DOMAIN
    logger.info(f"[COOKIE] Domain resolved to: {domain}")
    return domain



def set_auth_cookie(response, token):
    """
     Sets the JWT token in an HttpOnly cookie with flexible settings.
    """
    domain = determine_cookie_domain()

    # Load Secure, SameSite, Path from settings (could be .env-driven)
    secure = settings.COOKIE_SECURE
    samesite = settings.COOKIE_SAMESITE
    path = settings.COOKIE_PATH

    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,         #  HttpOnly for security
        secure=secure,         #  HTTPS if True
        samesite=samesite,     #  Allow flexible SameSite
        domain=domain,         #  Domain logic centralized
        path=path,             #  Include path flexibility
    )
    logger.info(f"[COOKIE] JWT token set: Domain={domain}, Secure={secure}, SameSite={samesite}, Path={path}")
    return response

def delete_auth_cookie(response):
    """
     Deletes the JWT token cookie.
    """
    domain = determine_cookie_domain()

    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        domain=domain,
    )
    logger.info(f"[COOKIE] JWT token cookie deleted for domain: {domain}")
    return response