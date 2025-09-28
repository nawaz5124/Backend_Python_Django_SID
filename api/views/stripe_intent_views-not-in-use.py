from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from api.services.stripe_intent_service import create_or_get_payment_intent

class StripePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get("amount")
        currency = request.data.get("currency", "GBP")

        if not amount:
            return Response({"error": "Amount is required."}, status=400)

        result = create_or_get_payment_intent(amount, currency)
        return Response(result)