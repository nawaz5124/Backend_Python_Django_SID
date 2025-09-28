from rest_framework import serializers

class StripePaymentIntentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        min_value=1,  # Ensure the amount is positive
        error_messages={"min_value": "Amount must be greater than 0."}
    )
    currency = serializers.ChoiceField(
        choices=["USD", "GBP", "EUR"],  # Restrict to valid currency codes
        error_messages={"invalid_choice": "Currency must be one of: USD, GBP, EUR."}
    )