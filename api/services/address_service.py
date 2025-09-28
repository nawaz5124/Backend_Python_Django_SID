from api.models.address_model import AddressModel
import logging

logger = logging.getLogger(__name__)


def process_address(donor, address_details):
    """
    Update or create an address for the donor.
    Handles address-related operations.
    """
    logger.info(f"INFO [Address Service]: AddressModel: ")
    logger.debug("DEBUG [Address Service]: AddressModel: ")

    AddressModel.objects.update_or_create(
        donor=donor,
        defaults={
            "first_line": address_details.get("firstLine", ""),
            "street": address_details.get("street", ""),
            "city": address_details.get("city", ""),
            "county": address_details.get("county", ""),
            "postcode": address_details.get("postcode", ""),
        },
    )