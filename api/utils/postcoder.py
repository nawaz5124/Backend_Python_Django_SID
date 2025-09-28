import requests
from django.conf import settings


def fetch_address_from_postcoder(postcode):
    """
    Fetch a list of addresses from the Postcoder API for a given postcode.
    """
    try:
        # Construct the full API URL
        url = f"{settings.POSTCODER_BASE_API_URL}/{postcode}?format=json"
        headers = {"Content-Type": "application/json"}

        # Make the request to Postcoder API
        response = requests.get(url, headers=headers)

        # Handle response
        if response.status_code == 200:
            return response.json()  # Return JSON data
        else:
            return {"error": f"Postcoder API error: {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}
