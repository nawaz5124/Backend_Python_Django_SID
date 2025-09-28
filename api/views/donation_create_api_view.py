from django.db import transaction
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
from api.utils.jwt_custom_authentication import jwt_required
from api.utils.donation_payload_logger import (
    log_donation_payload,
    update_logged_payload_from_donation,
)
import logging

logger = logging.getLogger(__name__)

@api_view(["POST"])  #  Restrict this API to POST requests
@jwt_required  #  Apply the custom JWT authentication decorator
def create_donation_api(request):
    """
    API endpoint to create a donation and process payments.
    """

    logger.info(f"[Donation Create Api View] Received donation request payload: %s", request.data)  #  Log the incoming request

    try:
        #  Step 1: Validate incoming request data
        validated_data = preprocess_and_validate_payload(request.data)

        #  Log the full original payload before processing
        log_donation_payload(
            data=request.data, 
            ip=request.META.get('REMOTE_ADDR'), 
            user_agent=request.META.get('HTTP_USER_AGENT')
        )

        #  Step 2: Process donor details (existing or new donor)
        donor = process_donor(validated_data["personalDetails"])
        logger.info(f"[Donation Create Api View] - Donor processed and saved: {donor.cft_no}")
        donorId = donor.cft_no;
        logger.info(f"[Donation Create Api View] - Donor processed, saved and Donor ID: {donorId}")
        emailId = donor.email
        logger.info(f"[Donation Create Api View] - Donor processed, saved and Email ID: {emailId}")


        #  Step 3: Process and save address details
        process_address(donor, validated_data["addressDetails"])
        logger.info(f"[Donation Create Api View] - Address processed successfully.")

        #  Step 4: Process donation & payment inside a database transaction
        with transaction.atomic():
            donation = process_donation(donor, validated_data)  #  Save donation entry 
            donationId = donation.donation_id;           
            logger.info(f"[Donation Create Api View] - Donor processed, saved and Donation ID : {donationId}")
            process_payment(donation=donation, payment_details=validated_data["paymentDetails"])  #  Store payment details

            metadata = {
                "donation_id": donationId,
                "donor_id": donorId,
            }
            logger.info(f"[Donation Create Api View] - Donor processed, saved and metadata : {metadata}")

            # After everything succeeds, update the payload row
            payment_ref = validated_data["paymentDetails"]["paymentReference"]
            update_logged_payload_from_donation(payment_ref)

    
        # Step 5: Return success response
        return build_success_response(donor, donation)

    except ValidationError as e:
        logger.error(f"[Donation Create Api View] - Validation error: {e.detail}")  #  Log validation issues
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    except BaseAPIException as e:
        logger.error(f"[Donation Create Api View] - Custom Exception: {str(e)}")  #  Log custom API exceptions
        return e.to_response()

    except Exception as e:
        logger.error(f"[Donation Create Api View] - Unhandled Exception: {str(e)}")  #  Log unexpected issues
        return Response(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )




def preprocess_and_validate_payload(data):
    """
    Preprocess and validate the incoming donation request payload.
    """
    data["donationDetails"] = data.get("donationDetails", {})  #  Ensure donation details exist
    data["paymentPlanDetails"] = data.get("paymentPlanDetails", {})  #  Ensure payment plan details exist

    #  Ensure donation frequency is provided (default: "One-Off")
    data["donationDetails"]["donationFrequency"] = data["paymentPlanDetails"].get("donationFrequency", "One-Off")

    #  Validate using serializer
    serializer = DonationRequestSerializer(data=data)
    if not serializer.is_valid():
        logger.error(f"[Donation Create Api View] Validation failed: %s", serializer.errors)  #  Log validation errors
        raise ValidationError(serializer.errors)

    logger.info(f"[Donation Create Api View] Validated donation request payload.")  #  Log successful validation
    return serializer.validated_data


def build_success_response(donor, donation):
    """
    Build and return a structured success response.
    """
    return Response(
        {
            "message": " Donation created successfully!",  #  Success message
            "donor": donor.cft_no,  #  Donor ID reference
            "donation": donation.donation_id,  #  Donation ID reference
        },
        status=status.HTTP_201_CREATED,
    )