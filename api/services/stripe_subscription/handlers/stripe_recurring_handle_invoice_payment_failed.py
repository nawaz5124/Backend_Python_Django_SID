import logging
from api.models.stripe_subscription_audit_model import StripeSubscriptionAudit
from api.services.stripe_subscription.handlers.stripe_recurring_handle_donation_backfill_service import backfill_recurring_donation_and_payment

logger = logging.getLogger(__name__)

def invoice_payment_failed(invoice_data):
    subscription_id = invoice_data.get("subscription")
    if not subscription_id:
        logger.warning(" No subscription ID found in invoice. Likely a manual or test invoice.")
    invoice_id = invoice_data.get("id")
    payment_intent = invoice_data.get("payment_intent")

    logger.warning(" Handling payment failure for recurring subscription")
    logger.info(f" Subscription ID: {subscription_id}")
    logger.info(f" Invoice ID: {invoice_id}")
    logger.info(f" Payment Intent: {payment_intent}")

    try:
        # Update audit table entry to reflect failure
        audit_entry = StripeSubscriptionAudit.objects.filter(
            subscription_id=subscription_id,
            payment_intent_id=payment_intent
        ).order_by('-created_at').first()
        

        
        if audit_entry:
            audit_entry.status = "failed"
            audit_entry.notes = "Recurring payment failed"
            audit_entry.save(update_fields=["status", "notes"])
            logger.info(" Audit record updated to 'failed'")

            #  Only backfill if audit entry update is successful
            backfill_recurring_donation_and_payment(event=invoice_data, status="Failed")

        else:
            logger.warning(" No matching audit record found to update")

        # Optionally: Notify user/admin here
        # send_failure_email_to_user(subscription_id)

    except Exception as e:
        logger.exception(" Exception while updating audit record for payment failure")