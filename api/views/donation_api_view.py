from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from api.serializers.donation_request_serializer import DonationRequestSerializer
from api.services.donor_service import process_donor
from api.services.address_service import process_address
from api.services.donation_service import process_donation
from api.services.payment_service import process_payment
from api.exceptions import BaseAPIException

import logging


logger = logging.getLogger(__name__)

@api_view(["POST"])
def create_donation_api(request):
    """
    API endpoint to create a donation.
    """
    logger.info("Received donation request payload: %s", request.data)

    try:
        # Pre-process the payload
        data = request.data
        data["donationDetails"] = data.get("donationDetails", {})
        data["paymentPlanDetails"] = data.get("paymentPlanDetails", {})
        data["donationDetails"]["donationFrequency"] = data["paymentPlanDetails"].get("donationFrequency", "One-Off")

        # Validate the payload using the serializer
        serializer = DonationRequestSerializer(data=data)
        if not serializer.is_valid():
            logger.error("Validation failed: %s", serializer.errors)
            raise ValidationError(serializer.errors)

        validated_data = serializer.validated_data
        logger.info("Validated donation request payload: %s", validated_data)

        # Process each layer
        donor = process_donor(validated_data["personalDetails"])
        process_address(donor, validated_data["addressDetails"])
        donation = process_donation(donor, validated_data)
        payment = process_payment(donation, validated_data["paymentDetails"])

        # Return success response
        return Response(
            {
                "message": "Donation created successfully.",
                "donor": donor.cft_no,
                "donation": donation.donation_id,
                "payment": payment.payment_id,
            },
            status=status.HTTP_201_CREATED,
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e.detail}")  # e.detail will now work with DRF's ValidationError
        return Response(
            {"error": e.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except BaseAPIException as e:
        logger.error(f"Custom Exception: {str(e)}")
        return e.to_response()

    except Exception as e:
        logger.error(f"Unhandled Exception: {str(e)}")
        return Response(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

