from api.models.donations_model import DonationModel
from api.exceptions import ValidationError, BaseAPIException
import logging

logger = logging.getLogger(__name__)

def process_donation(donor, data):
    """
    Create a donation entry in the database.
    Ensures both `fund` and `cause` are provided.
    Handles GDPR, CFT fund, and gift aid consents.
    """
    logger.info(f"INFO: [Donation Service] - Starting process_donation")
    logger.debug(f"DEBUG: [Donation Service] - process_donation called with donor: {donor} and data: {data}")

    try:
        # Extract donation details FIRST
        donation_details = data.get("donationDetails", {})
        if not donation_details:
            logger.error("ERROR: [Donation Service] - Missing donationDetails in payload")
            raise ValidationError("Missing required donationDetails in the payload")

        # Extract fund and cause correctly
        donation_type = donation_details.get("fund", "option_not_selected")  #  Fixed field
        donation_cause = donation_details.get("cause", "option_not_selected")

        # Validate: Ensure both `fund` and `cause` are provided
        if donation_type == "option_not_selected" or donation_cause == "option_not_selected":
            logger.error("ERROR: [Donation Service] - Both 'fund' and 'cause' must be selected.")
            raise ValidationError("Both 'fund' and 'cause' are required.")

        #  Extract payment details only AFTER validating fund and cause
        payment_details = data.get("paymentDetails", {})
        payment_intent_id = payment_details.get("paymentReference", None)
        logger.info(f"Info: [Donation Service] - payment_intent_id: {payment_intent_id}")

        # Log resolved values
        logger.debug(f"DEBUG: [Donation Service] - donation_type: {donation_type}, donation_cause: {donation_cause}, payment_intent_id: {payment_intent_id}")

        # Create the donation entry in the database
        donation = DonationModel.objects.create(
            donor=donor,
            donation_type=donation_type,
            donation_cause=donation_cause,
            amount=donation_details["amount"],
            donation_frequency=data["paymentPlanDetails"].get("donationFrequency", "One-Off"),
            
            gdpr_consent=donation_details.get("gdprConsent", False),
            gift_aid_consent=donation_details.get("giftAidConsent", False),
            cft_fund_consent=donation_details.get("cftFundConsent", False),
            receipt_generated=False,
            donation_status="Pending",
            payment_intent_id=payment_intent_id,  #  Move this AFTER donation details validation
        )

        logger.info(f"INFO: [Donation Service] - Donation created successfully: {donation}")
        return donation

    except KeyError as e:
        logger.error(f"ERROR: [Donation Service] - Missing key in donationDetails: {str(e)}")
        raise ValidationError(f"Missing key in donationDetails: {str(e)}")

    except Exception as e:
        logger.error(f"ERROR: [Donation Service] - An error occurred while processing the donation: {str(e)}")
        raise BaseAPIException(f"[Donation Service] - An error occurred while processing the donation: {str(e)}")