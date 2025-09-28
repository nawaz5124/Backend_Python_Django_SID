import stripe
import logging
from django.conf import settings

# Setup logger
logger = logging.getLogger(__name__)

# Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount, currency, emailId=None, metadata=None):
    logger.info(f"[Stripe] create_payment_intent called")
    logger.info(f"[Stripe] Creating intent for amount: {amount}, currency: {currency}")
    logger.info(f"[Stripe] Email (for receipt): {emailId}")
    logger.info(f"[Stripe] Metadata: {metadata}")

    try:
        #  Step 1: Create Stripe Customer (1‑time per donation)
        customer = stripe.Customer.create(
            email=emailId,
            metadata=metadata or {},
        )
        logger.info(f"[Stripe] Stripe Customer created: {customer.id}")

        #  Step 2: Create the PaymentIntent tied to the customer
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=["card"],
            customer=customer.id,           #  Link intent to customer
            receipt_email=emailId,
            metadata=metadata or {}
        )

        logger.info(f"[Stripe] PaymentIntent created successfully: {intent.id}")
        return intent

    except Exception as e:
        logger.error(f"[Stripe]  Error creating PaymentIntent: {str(e)}")
        raise


def retrieve_payment_intent(payment_intent_id):
    logger.info(f"[Stripe] retrieve_payment_intent called for ID: {payment_intent_id}")
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        logger.info(f"[Stripe] Retrieved PaymentIntent: {intent.id} with status: {intent.status}")
        return intent

    except Exception as e:
        logger.error(f"[Stripe] Error retrieving PaymentIntent {payment_intent_id}: {str(e)}")
        raise