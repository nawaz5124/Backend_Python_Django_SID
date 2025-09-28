
from rest_framework import serializers


class PersonalDetailsSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, error_messages={"required": "Title is required."})
    firstName = serializers.CharField(required=True, error_messages={"required": "First name is required."})
    lastName = serializers.CharField(required=True, error_messages={"required": "Last name is required."})
    orgName = serializers.CharField(required=False, allow_blank=True, error_messages={"blank": "Cannot be blank."})
    email = serializers.EmailField(required=True, error_messages={"required": "Email is required.", "invalid": "Enter a valid email."})
    mobile = serializers.CharField(required=True, error_messages={"required": "Mobile number is required."})
    stripeCustomerId = serializers.CharField(required=False, allow_blank=True)