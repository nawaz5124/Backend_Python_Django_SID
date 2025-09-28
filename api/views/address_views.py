import json
import logging
from django.http import JsonResponse
from rest_framework.decorators import api_view
from api.utils.jwt_custom_authentication import jwt_required  # Import the custom authentication decorator
from api.utils.postcoder import fetch_address_from_postcoder  # Import the address lookup function

logger = logging.getLogger(__name__)

@api_view(["POST"])
@jwt_required  #  Apply the custom JWT authentication decorator
def address_lookup(request):
    """
    Handles /api/address/lookup endpoint.
    Fetches address details based on a given postcode.
    Uses the custom JWT authentication decorator for security.
    """

    # 🔍 Debugging Logs
    logger.info(f"🔍 Address Lookup API Called")

    try:
        #  Extract JSON data from request
        data = json.loads(request.body)
        postcode = data.get("postcode")

        #  If postcode is missing, return an error
        if not postcode:
            logger.warning(" Missing postcode in request")
            return JsonResponse({"error": "Postcode is required"}, status=400)

        #  Fetch address details using the postcoder function
        address_data = fetch_address_from_postcoder(postcode)

        #  If no address found, return an error
        if not address_data:
            logger.info(f" No address found for postcode: {postcode}")
            return JsonResponse({"error": "No address found for the given postcode"}, status=404)

        #  Success: Return address data
        logger.info(f" Address lookup successful for postcode: {postcode}")
        return JsonResponse({"success": True, "data": address_data}, status=200)

    except json.JSONDecodeError:
        logger.error(" Invalid JSON format in request")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.error(f" Unexpected error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)