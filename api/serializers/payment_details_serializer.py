from rest_framework import serializers

class PaymentDetailsSerializer(serializers.Serializer):
    paymentMode = serializers.CharField(
        required=True,
        error_messages={
            "required": "Payment mode is required (e.g., Card, Cash).",
            "blank": "Payment mode cannot be blank."
        }
    )
    currency = serializers.CharField(
        required=True,
        error_messages={
            "required": "Currency is required (e.g., GBP, USD).",
            "blank": "Currency cannot be blank."
        }
    )
    paymentReference = serializers.CharField(
        required=True,  #  Always required: Holds `payment_intent_id`
        error_messages={
            "required": "Payment reference (payment_intent_id) is required.",
        }
    )
    transactionId = serializers.CharField(
        required=False,  #  Webhook will populate this later
        allow_blank=True,
        error_messages={
            "blank": "Transaction ID can be left blank if not applicable."
        }
    )

    def validate(self, data):
        """
        Ensures paymentReference (payment_intent_id) is always present,
        but transactionId is only updated via Stripe Webhook.
        """
        if data["paymentMode"] == "Card":
            if not data["paymentReference"]:
                raise serializers.ValidationError({
                    "paymentReference": "Payment reference (Stripe payment_intent_id) is required for card payments."
                })

            #  Do NOT check transactionId → It will be updated via webhook
        return data