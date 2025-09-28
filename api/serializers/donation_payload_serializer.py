from rest_framework import serializers
from api.models import DonationPayload

class DonationPayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationPayload
        fields = '__all__'