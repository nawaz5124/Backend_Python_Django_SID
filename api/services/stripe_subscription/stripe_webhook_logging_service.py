# stripe_logging_service.py

from datetime import datetime
from django.utils.timezone import now
from api.models.stripe_subscription_audit_model import StripeSubscriptionAudit
import logging

logger = logging.getLogger(__name__)

def log_to_subscription_audit(event: dict):
    try:
        obj = event.get("data", {}).get("object", {})
        lines = obj.get("lines", {}).get("data", [])
        line_item = lines[0] if lines else {}
        price_info = line_item.get("price", {}) or {}
        recurring_info = price_info.get("recurring", {}) or {}
        invoice_id = obj.get("id", "NA")

        line_item_description = line_item.get("description", "N/A")
        line_item_price = price_info.get("id", "N/A")

        logger.info(f" Logging event (invoice_id: {invoice_id}) to StripeSubscriptionAudit: {event['type']}")
        logger.info(f" Line Item Description: {line_item_description}")
        logger.info(f" Line Item Price ID: {line_item_price}")

        StripeSubscriptionAudit.objects.create(
            stripe_event_id=event.get("id"),
            event_type=event.get("type"),
            subscription_id=obj.get("subscription") or obj.get("parent", {}).get("subscription_details", {}).get("subscription") or "NA",
            payment_intent_id=obj.get("payment_intent"),
            price_id=price_info.get("id"),
            amount=obj.get("amount_due"),
            currency=obj.get("currency"),
            interval=recurring_info.get("interval"),
            plan_type=price_info.get("type"),
            description=line_item_description,
            billing_reason=obj.get("billing_reason"),
            collection_method=obj.get("collection_method"),
            customer_id=obj.get("customer"),
            customer_name=obj.get("customer_name"),
            customer_email=obj.get("customer_email"),
            invoice_url=obj.get("hosted_invoice_url"),
            invoice_status=obj.get("status"),
            livemode=event.get("livemode", False),
            created_at=datetime.fromtimestamp(event.get("created")) if event.get("created") else now(),
            webhook_received_at=now(),
            status="pending",
            notes="NA",
            raw_event_payload=event
        )
        logger.info(" Event logged to StripeSubscriptionAudit")
    except Exception as e:
        logger.warning(f" Failed to log StripeSubscriptionAudit: {e}")