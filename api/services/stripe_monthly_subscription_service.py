import logging
from django.utils.timezone import now
from django.utils.timezone import make_aware

from api.models import PaymentModel
from datetime import datetime
from api.services.payment_service import update_payment_from_subscription_webhook
import json

from api.services.stripe_subscription.handle_invoice_payment_failed import handle_invoice_payment_failed
from api.services.stripe_subscription.handle_subscription_deleted import handle_subscription_deleted

#  Add more imports when needed
# from services.stripe_subscription.handle_subscription_deleted import handle_subscription_deleted
# from services.stripe_subscription.handle_customer_created import handle_customer_created

logger = logging.getLogger(__name__)


def handle_invoice_paid(event):
    logger.info(" [Webhook - Monthly Subscription - handle_invoice_paid] Starting invoice.paid handler")

    try:
        invoice = event.get("data", {}).get("object", {})
        subscription_id = invoice.get("subscription")
      #  payment_reference = invoice.get("payment_intent") . #  Uncomment if you need payment_reference
      #  logger.info(f" Extracted payment_reference: {payment_reference}")        
        logger.info(f" Extracted subscription_id: {subscription_id}")
        #logger.info(f" Full Invoice Payload: {json.dumps(invoice, indent=2)}")
        logger.info(f" Full Invoice Payload:")

        if not subscription_id:
            logger.warning(" Missing subscription_id in invoice data")
            return

        # Call centralized payment update logic
        update_payment_from_subscription_webhook(subscription_id, invoice)

        logger.info(f" [Webhook] Payment updated successfully for subscription_id: {subscription_id}")

    except Exception as e:
        logger.exception(f" [handle_invoice_paid] Unexpected error: {str(e)}")


def process_subscription_event(event_type, event):
    if event_type == "invoice.payment_failed":
        handle_invoice_payment_failed(event)

    #elif event_type == "customer.subscription.deleted":
    #     handle_subscription_deleted(event)

    #elif event_type == "customer.created":
    #    handle_customer_created(event)

    else:
        print(f" Unhandled event type: {event_type}")

def handle_subscription_deleted(event):
    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")
    logger.info(f"📉 Subscription deleted: {subscription_id}")

    try:
        payment = PaymentModel.objects.filter(stripe_subscription_id=subscription_id).latest("created_at")
        payment.payment_status = "Cancelled"
        payment.updated_at = now()
        payment.save()
        logger.info(f" Updated payment as Cancelled for subscription: {subscription_id}")
    except PaymentModel.DoesNotExist:
        logger.warning(f" No payment found for deleted subscription {subscription_id}")


def handle_subscription_updated(event):
    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    logger.info(f" Subscription updated: {subscription_id} → status: {status}")

    try:
        payment = PaymentModel.objects.filter(stripe_subscription_id=subscription_id).latest("created_at")
        payment.payment_status = status.capitalize()
        payment.updated_at = now()
        subscription_data = event.get("data", {}).get("object", {})
        payment.subscription_status = subscription_data.get("status")
        payment.next_billing_date = datetime.fromtimestamp(subscription_data.get("current_period_end"))
        payment.metadata_json = subscription_data.get("metadata")
        payment.save()
        logger.info(f" PaymentModel updated with new status: {status}")
    except PaymentModel.DoesNotExist:
        logger.warning(f" No payment found for updated subscription {subscription_id}")


def log_customer_event(event):
    customer = event["data"]["object"]
    logger.info(f" Stripe Customer Event: ID={customer['id']}, Email={customer.get('email')}")

def handle_customer_created(event_obj):
    customer_id = event_obj.get("id")
    email = event_obj.get("email")
    logger.info(f" [customer.created] New customer created: {customer_id}, {email}")

def handle_customer_updated(event_obj):
    customer_id = event_obj.get("id")
    logger.info(f" [customer.updated] Customer updated: {customer_id}")