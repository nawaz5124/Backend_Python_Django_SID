from rest_framework import serializers
from api.serializers.personal_details_serializer import PersonalDetailsSerializer
from api.serializers.address_details_serializer import AddressDetailsSerializer
from api.serializers.donation_details_serializer import DonationDetailsSerializer
from api.serializers.payment_details_serializer import PaymentDetailsSerializer
from api.serializers.payment_plan_serializer import PaymentPlanDetailsSerializer


class DonationRequestSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # Debugging statement to confirm which file is being used
        print("donations_request_serializer - Using DonationRequestSerializer from", __file__)
        super().__init__(*args, **kwargs)

    # Replace DictField with group-level serializers
    personalDetails = PersonalDetailsSerializer(
        required=True, 
        error_messages={"required": "Personal details are required."}
    )
    addressDetails = AddressDetailsSerializer(
        required=True, 
        error_messages={"required": "Address details are required."}
    )
    donationDetails = DonationDetailsSerializer(
        required=True, 
        error_messages={"required": "Donation details are required."}
    )
    paymentDetails = PaymentDetailsSerializer(
        required=True, 
        error_messages={"required": "Payment details are required."}
    )
    paymentPlanDetails = PaymentPlanDetailsSerializer(
        required=True, 
        error_messages={"required": "Payment plan details are required."}
    )