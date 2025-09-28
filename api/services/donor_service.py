import logging
from api.models.donors_model import DonorModel
from api.utils.generate_cft_no import generate_cft_no
from api.exceptions import BaseAPIException, ValidationError

logger = logging.getLogger(__name__)

def process_donor(personal_details):
    """
    Check for existing donor or create a new one.
    Handles donor-related operations, including checking for existing donors and creating new ones.
    """
    try:
        # Ensure email and mobile are present and not empty
        donor = DonorModel.objects.filter(
            email=personal_details.get("email")
        ).first() or DonorModel.objects.filter(
            mobile=personal_details.get("mobile")  # Changed to use .get() method
        ).first()

        if donor:
            logger.info(f"Existing donor found: {donor.first_name} {donor.last_name} (CFT No: {donor.cft_no})")
            return donor
        else:
            # Create a new donor
            return DonorModel.objects.create(
                cft_no=generate_cft_no(),
                title=personal_details.get("title", ""),
                first_name=personal_details["firstName"],
                last_name=personal_details["lastName"],
                org_name=personal_details.get("orgName", ""),
                email=personal_details["email"],
                mobile=personal_details.get("mobile"),  # Changed to use .get() method
                stripe_customer_id=personal_details.get("stripeCustomerId", ""),
            )
    except KeyError as e:
        raise ValidationError(f"Missing key in personalDetails: {str(e)}")
    except Exception as e:
        raise BaseAPIException(f"An error occurred while processing the donor: {str(e)}")