import logging
from api.models.stripe_subscription_audit_model import StripeSubscriptionAudit
from api.services.stripe_subscription.handlers.stripe_recurring_handle_donation_backfill_service import backfill_recurring_donation_and_payment

logger = logging.getLogger(__name__)

def handle_recurring_invoice_paid(invoice_data):
    logger.info(" [Recurring] invoice.paid triggered")

    invoice_id = invoice_data.get("id")
    customer_id = invoice_data.get("customer")
    subscription_id = invoice_data.get("subscription")
    payment_intent = invoice_data.get("payment_intent")
    amount_paid = invoice_data.get("amount_paid")
    status = invoice_data.get("status")
    hosted_invoice_url = invoice_data.get("hosted_invoice_url")

    try:
        #  Locate matching audit record
        audit_entry = StripeSubscriptionAudit.objects.filter(
            subscription_id=subscription_id,
            payment_intent_id=payment_intent
        ).order_by("-created_at").first()

        if audit_entry:
            audit_entry.status = "paid"
            audit_entry.notes = "Recurring payment success"
            audit_entry.save(update_fields=["status", "notes"])
            logger.info(" Audit record updated to 'paid'")

            #  Perform backfill only if audit is found
            backfill_recurring_donation_and_payment(event=invoice_data, status="Paid")
            logger.info(" Donation and Payment backfill completed successfully")

        else:
            logger.warning(" No matching audit record found for backfill")

    except Exception as e:
        logger.exception(" Exception occurred while handling recurring invoice.paid")

    #  Log key payload details
    logger.info(f" Invoice ID: {invoice_id}")
    logger.info(f" Customer ID: {customer_id}")
    logger.info(f" Subscription ID: {subscription_id}")
    logger.info(f" Amount Paid: {amount_paid}")
    logger.info(f" Invoice Status: {status}")
    logger.info(f" Invoice URL: {hosted_invoice_url}")

    return {"message": "invoice.paid handler executed"}