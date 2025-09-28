import logging
from django.utils.timezone import now
from api.models import PaymentModel

logger = logging.getLogger(__name__)

def handle_subscription_deleted(event):
    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")

    logger.info(f" Subscription deleted: {subscription_id}")

    try:
        payment = PaymentModel.objects.filter(
            stripe_subscription_id=subscription_id
        ).latest("created_at")

        payment.payment_status = "Cancelled"
        payment.updated_at = now()
        payment.save()

        logger.info(f" Marked payment as Cancelled for subscription {subscription_id}")

    except PaymentModel.DoesNotExist:
        logger.warning(f" No PaymentModel found for deleted subscription_id: {subscription_id}")