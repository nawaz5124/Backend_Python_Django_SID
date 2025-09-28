
import logging
from rest_framework import serializers

logger = logging.getLogger(__name__)

class StripeSubscriptionIntentSerializer(serializers.Serializer):
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    amount = serializers.IntegerField(min_value=1)
    cause = serializers.CharField()
    donationFrequency = serializers.CharField()

    def validate(self, data):
        logger.debug(f"🔍 Validating subscription payload: {data}")
        
        # Custom logic (if any)
        if data['amount'] < 5:
            logger.warning(" Donation amount too low for subscription.")
        
        return data