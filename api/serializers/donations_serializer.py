from rest_framework import serializers

# Payment Plan Details Serializer
class PaymentPlanDetailsSerializer(serializers.Serializer):
    paymentFrequency = serializers.CharField(required=True)  # One-Off or Recurring
    isRecurring = serializers.BooleanField(required=True)

# Personal Details Serializer
class PersonalDetailsSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    firstName = serializers.CharField(required=True)
    lastName = serializers.CharField(required=True)
    orgName = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True, allow_blank=False)  # Ensure email is required and not blank
    mobile = serializers.CharField(required=True, allow_blank=False)  # Ensure mobile is required and not blank
    stripeCustomerId = serializers.CharField(required=False, allow_blank=True)

# Address Details Serializer
class AddressDetailsSerializer(serializers.Serializer):
    firstLine = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    county = serializers.CharField(required=False, allow_blank=True)
    postcode = serializers.CharField(required=True)

# Donation Details Serializer
class DonationDetailsSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)  # Zakath, Sadaqah, etc.
    cause = serializers.CharField(required=True)  # Education Support, etc.
    amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
    gdprConsent = serializers.BooleanField(required=True)
    cftFundConsent = serializers.BooleanField(required=True)

# Gift Aid Details Serializer
class GiftAidDetailsSerializer(serializers.Serializer):
    giftAidConsent = serializers.BooleanField(required=True)

# Payment Details Serializer
class PaymentDetailsSerializer(serializers.Serializer):
    paymentMode = serializers.CharField(required=True)  # Card, Cash, etc.
    currency = serializers.CharField(required=True)  # GBP, USD, etc.
    paymentReference = serializers.CharField(required=True, allow_blank=True)
    transactionId = serializers.CharField(required=False, allow_blank=True)

# Main Request Serializer
class DonationRequestSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        print("donations_serilazer - Using DonationRequestSerializer from", __file__)
        super().__init__(*args, **kwargs)
    paymentPlanDetails = PaymentPlanDetailsSerializer()
    personalDetails = PersonalDetailsSerializer()
    addressDetails = AddressDetailsSerializer()
    donationDetails = DonationDetailsSerializer()
    giftAidDetails = GiftAidDetailsSerializer()
    paymentDetails = PaymentDetailsSerializer()

    def validate(self, data):
        # Ensure all required groups are present
        if not data.get("paymentPlanDetails"):
            raise serializers.ValidationError({"paymentPlanDetails": "This field is required."})
        if not data.get("personalDetails"):
            raise serializers.ValidationError({"personalDetails": "This field is required."})
        if not data.get("addressDetails"):
            raise serializers.ValidationError({"addressDetails": "This field is required."})
        if not data.get("donationDetails"):
            raise serializers.ValidationError({"donationDetails": "This field is required."})
        if not data.get("giftAidDetails"):
            raise serializers.ValidationError({"giftAidDetails": "This field is required."})
        if not data.get("paymentDetails"):
            raise serializers.ValidationError({"paymentDetails": "This field is required."})

        # Additional Validation Logic (if required)
        if data["donationDetails"]["amount"] <= 0:
            raise serializers.ValidationError({"donationDetails": "Donation amount must be greater than zero."})

        return data