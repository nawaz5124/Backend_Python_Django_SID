from rest_framework import serializers

from api.models.payments_model import PaymentModel


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentModel
    """

    class Meta:
        model = PaymentModel
        fields = [
            "payment_id",
            "donation",
            "amount",
            "currency",
            "payment_mode",
            "payment_status",
            "transaction_id",
            "stripe_payment_intent_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["payment_id", "created_at", "updated_at"]

    def validate(self, data):
        """
        Custom validation for PaymentSerializer
        """
        if not data.get("amount") or data["amount"] <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be greater than zero."}
            )

        if not data.get("currency"):
            raise serializers.ValidationError({"currency": "Currency is required."})

        if not data.get("payment_mode"):
            raise serializers.ValidationError(
                {"payment_mode": "Payment mode is required."}
            )

        return data
