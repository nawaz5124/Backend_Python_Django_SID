from rest_framework import serializers

class GiftAidDetailsSerializer(serializers.Serializer):
    giftAidConsent = serializers.BooleanField(required=False, default=False)
