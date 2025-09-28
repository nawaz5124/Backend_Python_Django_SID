import logging
from api.models.stripe_subscription_audit_model import StripeSubscriptionAudit

logger = logging.getLogger(__name__)


def handle_recurring_subscription_deleted(invoice_data):
    logger.info(" [Recurring] customer.subscription.deleted triggered")

    # Extract key details
    subscription_id = invoice_data.get("id")
    customer_id = invoice_data.get("customer")
    status = invoice_data.get("status")
    cancel_at = invoice_data.get("cancel_at")
    canceled_at = invoice_data.get("canceled_at")
    cancel_reason = invoice_data.get("cancellation_details", {}).get("reason", "Not provided")

    # Log extracted values
    logger.info(f" Subscription ID: {subscription_id}")
    logger.info(f" Customer ID: {customer_id}")
    logger.info(f" Status: {status}")
    logger.info(f" Cancel At: {cancel_at}")
    logger.info(f" Canceled At: {canceled_at}")
    logger.info(f" Cancel Reason: {cancel_reason}")

    return {"message": " stripe_recurring_handle_subscription_deleted executed"}