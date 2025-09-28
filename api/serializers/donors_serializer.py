from rest_framework import serializers

from api.models.donors_model import DonorModel


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorModel
        fields = "__all__"  # Expose all fields for now. Customize as needed.
