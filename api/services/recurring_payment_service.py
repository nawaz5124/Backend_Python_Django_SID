import logging

logger = logging.getLogger(__name__)

from api.services.stripe_monthly_subscription_service import (
    handle_invoice_paid,
    handle_invoice_payment_failed,
    handle_subscription_deleted,
)

def handle_recurring_payment(event):
    event_type = event.get("type")
    logger.info(f" [Recurring Handler] Processing event type: {event_type}")

    if event_type == "invoice.paid":
        handle_invoice_paid(event)

    elif event_type == "invoice.payment_failed":
        handle_invoice_payment_failed(event)

    elif event_type == "customer.subscription.deleted":
        handle_subscription_deleted(event['data']['object'])

    else:
        logger.warning(f" [Recurring Handler] Unhandled recurring event type: {event_type}")