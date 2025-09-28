# File: api/views/choices_api_view.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
def get_donation_choices(request):
    """
    API endpoint to return available choices for fund and cause fields.
    """
    try:
        from api.models.donations_model import fund_choices, cause_choices
        logger.debug("Fetching donation choices for fund and cause fields.")

        response_data = {
            "fund_choices": [choice[0] for choice in fund_choices],
            "cause_choices": [choice[0] for choice in cause_choices],
        }

        logger.info(f"Successfully fetched donation choices: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error while fetching donation choices: {str(e)}")
        return Response(
            {"error": "Unable to fetch donation choices."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )