from api.models.donations_model import DonationModel
import logging

logger = logging.getLogger(__name__)


def create_donation(donor, donation_details):
    """
    Creates a new donation entry in the database.
    """

    logger.info("INFO : DonationModel: ",donor)
    logger.debug("DEBUG : DonationModel: ",donation_details)
    return DonationModel.objects.create(
        donor=donor,
        donation_type=donation_details["type"],
        donation_cause=donation_details["cause"],
        amount=donation_details["amount"],
        donation_frequency=donation_details.get("donationFrequency", "One-Off"),
        gdpr_consent=donation_details.get("gdprConsent", False),
        cft_fund_consent=donation_details.get("cftFundConsent", False),
        gift_aid_consent=donation_details.get("giftAidConsent", False),
        receipt_generated=False,
        donation_status="Pending",
    )
