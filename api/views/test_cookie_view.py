import os
from decouple import config  # Ensure this is at the top

# test_cookie_view.py
from django.http import JsonResponse

# test_cookie_view.py
from django.http import JsonResponse

def test_cookie(request):
    """
     Sets a simple test cookie to check if Django can set cookies properly.
    """
    COOKIE_DOMAIN = config("COOKIE_DOMAIN", default="localhost")
    response = JsonResponse({"message": " Test cookie has been set!"})
    response.set_cookie(
        key="test_cookie_test",
        value="test_value_test",
        httponly=True,  # HttpOnly ensures it's not accessible by JavaScript
        secure=True,    #  Change to False for local testing
        samesite=None,  #  Allows cross-origin requests
        domain=COOKIE_DOMAIN,  #  Explicitly set for localhost testing
    )
    return response


def check_cookie(request):
    """
     Checks if Django can read cookies sent in the request.
    """
    cookies = request.COOKIES  # Get all available cookies
    return JsonResponse({
        "all_cookies": cookies,
        "test_cookie": cookies.get('test_cookie'),
        "access_token": cookies.get('access_token')
    })