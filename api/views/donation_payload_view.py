# views/donation_payload_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serializers.donation_payload_flat_serializer import DonationPayloadSerializer
from api.serializers.donation_request_serializer import DonationRequestSerializer

class DonationPayloadView(APIView):
    def post(self, request):
        # Validate grouped request
        validated_request = DonationRequestSerializer(data=request.data)
        if not validated_request.is_valid():
            return Response(validated_request.errors, status=status.HTTP_400_BAD_REQUEST)

        data = validated_request.validated_data
        flat_data = {
            #  Personal Info
            "title": data["personalDetails"]["title"],
            "first_name": data["personalDetails"]["firstName"],
            "last_name": data["personalDetails"]["lastName"],
            "org_name": data["personalDetails"].get("orgName"),
            "email": data["personalDetails"]["email"],
            "mobile": data["personalDetails"]["mobile"],
            "stripe_customer_id": data["personalDetails"].get("stripeCustomerId"),

            #  Address Info
            "first_line": data["addressDetails"]["firstLine"],
            "street": data["addressDetails"]["street"],
            "city": data["addressDetails"]["city"],
            "county": data["addressDetails"]["county"],
            "postcode": data["addressDetails"]["postcode"],

            #  Donation Info
            "fund": data["donationDetails"]["fund"],
            "cause": data["donationDetails"]["cause"],
            "amount": data["donationDetails"]["amount"],
            "gdpr_consent": data["donationDetails"]["gdprConsent"],
            "cft_fund_consent": data["donationDetails"]["cftFundConsent"],
            "gift_aid_consent": data["donationDetails"]["giftAidConsent"],

            #  Payment Info
            "paymentMode": data["paymentDetails"]["paymentMode"],
            "currency": data["paymentDetails"]["currency"],
            "payment_reference": data["paymentDetails"]["paymentReference"],
            "transaction_id": data["paymentDetails"].get("transactionId"),

            #  Plan Info
            "donation_frequency": data["paymentPlanDetails"]["donationFrequency"],

            #  Raw submission
            "submitted_payload": request.data
        }

        #  Save using model serializer
        serializer = DonationPayloadSerializer(data=flat_data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "message": "Donation payload captured ",
                "payload_id": instance.id,
                "status": instance.donation_status
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)