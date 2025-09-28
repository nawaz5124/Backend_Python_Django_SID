# services/stripe_subscription/handle_invoice_payment_failed.py
import logging
from django.utils.timezone import now
from api.models import PaymentModel

logger = logging.getLogger(__name__)

def handle_invoice_payment_failed(event):
    invoice = event["data"]["object"]
    logger.info(f" Invoice Payload: {invoice}")

    # Extract subscription ID and payment intent ID from the invoice
    subscription_id = invoice.get("subscription")
    payment_intent_id = invoice.get("payment_intent")

    if not subscription_id:
        logger.warning(f" Missing subscription_id, fallback to PaymentIntent: {payment_intent_id}")
        return

    logger.warning(f" Payment failed for subscription {subscription_id}")

    try:
        #  Fetch the most recent payment entry for this subscription
        payment = PaymentModel.objects.filter(
            stripe_subscription_id=subscription_id
        ).latest("created_at")

        #  Update status to 'Failed'
        payment.payment_status = "Failed"
        payment.updated_at = now()
        payment.save()

        #  Correct field used: payment.payment_id instead of payment.id
        logger.info(f" PaymentModel {payment.payment_id} marked as Failed.")

    except PaymentModel.DoesNotExist:
        logger.warning(f" No PaymentModel found for subscription_id: {subscription_id}")