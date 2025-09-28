from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import stripe
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def attach_payment_method_view(request):
    logger.info("Attach payment method API called")

    data = request.data
    payment_method_id = data.get("payment_method_id")
    stripe_customer_id = data.get("customer_id")

    if not payment_method_id or not stripe_customer_id:
        logger.warning("Missing payment_method_id or stripe_customer_id")
        return Response(
            {"error": "Missing required parameters"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Step 1 Attach the payment method to the customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=stripe_customer_id,
        )
        logger.info(f"Attached payment method {payment_method_id} to customer {stripe_customer_id}")

        # Step 2️ Set it as default for invoices
        stripe.Customer.modify(
            stripe_customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id,
            },
        )
        logger.info(f"Set default payment method for customer {stripe_customer_id}")

        return Response({"message": "Payment method attached successfully"}, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e.user_message}")
        return Response({"error": str(e.user_message)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Unexpected error while attaching payment method")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)