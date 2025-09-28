
from rest_framework import serializers

class AddressDetailsSerializer(serializers.Serializer):
    firstLine = serializers.CharField(
        required=True,
        error_messages={"required": "First line of the address is required."}
    )
    street = serializers.CharField(
        required=True,
        error_messages={"required": "Street is required."}
    )
    city = serializers.CharField(
        required=True,
        error_messages={"required": "City is required."}
    )
    county = serializers.CharField(
        required=False,
        allow_blank=True,
        error_messages={"blank": "County can be left blank but must be provided if applicable."}
    )
    postcode = serializers.CharField(
        required=True,
        error_messages={"required": "Postcode is required."}
    )