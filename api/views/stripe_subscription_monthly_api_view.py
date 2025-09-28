'''
POST /api/stripe/subscription-intent/ API is now implemented.

It performs:
	•	Stripe Customer creation
	•	Product + recurring Price setup
	•	Subscription creation with default_incomplete behavior
	•	Returns client_secret, subscription_id, payment_intent_id, and customer_id

CRITICAL FIXES IMPLEMENTED:
	•	payment_settings: save_default_payment_method
	•	setup_future_usage: off_session
	•	customer_id in response for frontend
'''
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from api.models import DonationModel, PaymentModel, StripeIntentModel  #  Add model
from api.serializers.stripe_subscriptionIntent_serializer import StripeSubscriptionIntentSerializer
import stripe
import logging
import traceback

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscription_intent_view(request):
    logger.info("🔄 Received subscription intent request")

    serializer = StripeSubscriptionIntentSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"❌ Invalid data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    email = validated.get("email")
    amount = validated.get("amount")
    cause = validated.get("cause")
    first_name = validated.get("firstName")
    last_name = validated.get("lastName")
    phone = validated.get("phone")
    fund = validated.get("fund")

    try:
        print("📋 Payload:", validated)

        # Step 1: Create Stripe customer
        customer = stripe.Customer.create(
            email=email,
            name=f"{first_name} {last_name}",
            phone=phone,                    # 📋 ADD: Better customer data
            description=f"Monthly Donor - {cause}", # 📋 ADD: Helpful for tracking
            metadata={                      # 📋 ADD: Custom tracking
                "source": "donation_website",
                "campaign": cause,
                "fund": fund
            }
        )
        logger.info(f"✅ Stripe customer created: {customer.id}")

        # Step 2: Create product and price
        product = stripe.Product.create(name=f"Donation - {cause}")
        price = stripe.Price.create(
            unit_amount=int(amount) * 100,
            currency="GBP",
            # recurring={"interval": "month"},  # Uncomment for monthly
            recurring={"interval": "day"},      # Keep for daily testing
            product=product.id,
            nickname=f"Monthly {fund} - £{amount}", # 📋 ADD: Easy identification
        )
        logger.info(f"✅ Stripe price created: {price.id}")

        # Step 3: Create subscription with CRITICAL PAYMENT METHOD SAVING
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price.id}],
            payment_behavior="default_incomplete",
            payment_settings={
                "save_default_payment_method": "on_subscription"  # 🔑 CRITICAL FIX #1
            },
            expand=["latest_invoice.payment_intent"],
                description=f"Monthly donation for {cause}", # 📋 ADD: Description
            metadata={                          # 📋 ADD: Tracking
                "Donor_email": email,
                "Cause": cause,
                "Fund": fund,
                "Amount": amount
            }
        )
        logger.info(f"✅ Subscription created: {subscription.id}")

        payment_intent = subscription.latest_invoice.payment_intent

        # Step 4: Modify PaymentIntent for off-session future payments
        stripe.PaymentIntent.modify(
            payment_intent.id,
            setup_future_usage="off_session",  # 🔑 CRITICAL FIX #2
                description=f"Initial payment for monthly {cause} donation", # 📋 ADD
                metadata={                          # 📋 ADD: Better tracking
                    "subscription_id": subscription.id,
                    "customer_email": email,
                    "donation_type": "recurring"
                }

        )
        logger.info(f"✅ PaymentIntent modified with setup_future_usage: {payment_intent.id}")

        client_secret = payment_intent.client_secret

        # Step 5: Create session record
        session = StripeIntentModel.objects.create(
            payment_intent_id=payment_intent.id,
            client_secret=client_secret,
            status=payment_intent.status,
            amount=amount,
            currency="GBP",
        )
        logger.info(f"✅ StripeIntentModel session created: {session.session_id}")

        # Step 6: Return response with customer_id for frontend
        return Response({
            "client_secret": client_secret,
            "subscription_id": subscription.id,
            "payment_intent_id": payment_intent.id,
            "customer_id": customer.id,  # 🔑 CRITICAL FIX #3 - Frontend needs this
            "session_id": str(session.session_id),
            "price_id": price.id,              # 📋 ADD: Useful for frontend
            "amount": amount,                  # 📋 ADD: Confirmation
            "currency": "GBP",                 # 📋 ADD: Confirmation
            "interval": "month"                # 📋 ADD: Billing frequecy
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("❌ Subscription creation failed due to exception:")
        traceback.print_exc()
        return Response({"detail": "Stripe error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)