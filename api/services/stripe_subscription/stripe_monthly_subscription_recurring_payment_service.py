import logging
from api.services.stripe_subscription.handlers import (
    stripe_recurring_handle_invoice_payment_failed,
    stripe_recurring_handle_invoice_paid,
    stripe_recurring_handle_subscription_deleted,
)
# Import specific function
from api.services.stripe_subscription.handlers.stripe_recurring_handle_invoice_payment_failed import invoice_payment_failed

# Use it
#invoice_payment_failed(invoice_data)
logger = logging.getLogger(__name__)

def handle_recurring_subscription_cycle(subscription_id, invoice_data, event_type):
    logger.info(" [Recurring] Handling subscription_cycle event")
    logger.info(f" Subscription ID: {subscription_id}")
    logger.info(f" Full Invoice Payload:")
  #  logger.info(f" Full Invoice Payload: {invoice_data}")
    logger.info(f" Stripe Event Type: {event_type}")

    if event_type == "invoice.payment_failed":
        logger.warning(" [Recurring] Subscription payment failed.")
        stripe_recurring_handle_invoice_payment_failed.invoice_payment_failed(invoice_data)


    elif event_type == "invoice.paid":
        logger.info(" [Recurring] Invoice paid successfully.")
        stripe_recurring_handle_invoice_paid.handle_recurring_invoice_paid(invoice_data)

    elif event_type == "customer.subscription.deleted":
        logger.warning(" [Recurring] Subscription cancelled.")
        stripe_recurring_handle_subscription_deleted.handle(invoice_data)

    else:
        logger.warning(f" [Recurring] Unhandled event type: {event_type}")