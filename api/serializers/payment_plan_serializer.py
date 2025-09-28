from rest_framework import serializers

class PaymentPlanDetailsSerializer(serializers.Serializer):
    donationFrequency = serializers.CharField(required=True)  # One-Off or Recurring
