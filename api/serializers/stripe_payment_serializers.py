from rest_framework import serializers
from api.models.stripe_intent_models import StripeIntentModel

class StripeIntentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeIntentModel
        fields = '__all__'