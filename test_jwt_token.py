import os
import django
import requests
from django.conf import settings

#  Ensure the correct settings module is used
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "donor_management.settings")

#  Add project root to Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#  Initialize Django
django.setup()

def get_internal_jwt_token():
    """
    Function to request an internal JWT token using API service credentials.
    """
    api_url = f"{settings.BACKEND_URL}/api/token/"
    payload = {
        "username": settings.API_SERVICE_USERNAME,
        "password": settings.API_SERVICE_PASSWORD,
    }

    print(f" Making request to: {api_url}")
    
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        print(" Token retrieved successfully!")
        return response.json().get("access")
    else:
        print(f" Failed to get token: {response.status_code} | {response.json()}")
        return None

if __name__ == "__main__":
    token = get_internal_jwt_token()
    if token:
        print(f" JWT Token: {token}")
    else:
        print(" Could not retrieve JWT token. Check credentials & API.")