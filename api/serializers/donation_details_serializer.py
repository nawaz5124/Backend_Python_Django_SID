from rest_framework import serializers
from api.models.donations_model import fund_choices, cause_choices

class DonationDetailsSerializer(serializers.Serializer):
    fund = serializers.ChoiceField(
        choices=[choice[0] for choice in fund_choices],
        required=True,  # Make it mandatory
        error_messages={
            "required": "Fund selection is required.",
            "invalid_choice": "Invalid fund selection. Must be one of the predefined choices.",
        }
    )
    cause = serializers.ChoiceField(
        choices=[choice[0] for choice in cause_choices],
        required=True,  # Make it mandatory
        error_messages={
            "required": "Cause selection is required.",
            "invalid_choice": "Invalid cause selection. Must be one of the predefined choices.",
        }
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            "required": "Donation amount is required.",
            "min_value": "Donation amount must be greater than 0.",
        }
    )
    gdprConsent = serializers.BooleanField(
        required=False,
        default=False,
        error_messages={
            "invalid": "GDPR Consent must be a boolean value."
        }
    )
    cftFundConsent = serializers.BooleanField(
        required=False,
        default=False,
        error_messages={
            "invalid": "CFT Fund Consent must be a boolean value."
        }
    )
    giftAidConsent = serializers.BooleanField(
        required=False,
        default=False,
        error_messages={
            "invalid": "Gift Aid Consent must be a boolean value."
        }
    )

    def validate(self, data):
        """
        Additional validation logic can be added here if needed.
        """
        # Ensure the amount is greater than zero
        if data.get("amount", 0) <= 0:
            raise serializers.ValidationError("Donation amount must be greater than 0.")

        return data