import stripe
import logging
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from api.models.stripe_subscription_audit_model import StripeSubscriptionAudit
from api.services.stripe_subscription.stripe_webhook_logging_service import log_to_subscription_audit  #  New helper
from api.services.stripe_monthly_subscription_service import (
    handle_invoice_payment_failed,
    handle_subscription_deleted,
    handle_invoice_paid,
    )
from django.utils.timezone import now  # Make sure this is imported
from datetime import datetime
#from api.services.recurring_payment_service import handle_recurring_payment
from api.services.stripe_subscription.stripe_monthly_subscription_recurring_payment_service import handle_recurring_subscription_cycle
logger = logging.getLogger(__name__)
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_subscription_webhook(request):
    logger.info(f" [Webhook] Incoming Stripe webhook call")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    logger.info(f" Stripe Signature Header: {sig_header}")
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_MONTHLY_SUBSCRIPTION_SECRET
        )
        logger.info(f" Stripe event verified: {event['type']}")
    except Exception as audit_error:
        logger.warning(f" Failed to log stripe.Webhook.construct_event: {audit_error}")
#  Always log the event to audit table
    try:
        obj = event.get("data", {}).get("object", {})
        lines = obj.get("lines", {}).get("data", [])
        line_item = lines[0] if lines else {}
        price_info = line_item.get("price", {}) or {}
        recurring_info = price_info.get("recurring", {}) or {}
        invoice_id = obj.get("id", "N/A")
        line_item_description = line_item.get("description", "N/A")
        line_item_price = price_info.get("id", "N/A")
        #  Always log the event to audit table
        log_to_subscription_audit(event)  #  call helper safely
    except Exception as audit_error:
        logger.warning(f" Failed to log StripeSubscriptionAudit: {audit_error}")
    except ValueError as e:
        logger.error(f" Invalid payload: {e}")
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f" Signature verification failed: {e}")
        return HttpResponseBadRequest("Invalid signature")
    except Exception as e:
        logger.exception(f" Unexpected error during webhook parsing: {e}")
        return HttpResponseBadRequest("Webhook error")
    #  Extract billing_reason early
    invoice_data = event.get("data", {}).get("object", {})
    billing_reason = invoice_data.get("billing_reason", "")
    subscription_id = invoice_data.get("subscription")
    try:
        #  Route based on billing_reason
        if billing_reason == "subscription_create":
            logger.info(" First-time subscription payment received.")
            handle_invoice_paid(event)
            
            #  Handle other creation-related events here
            if event['type'] == 'invoice.payment_failed':
                logger.info(f" Subscription payment failed. Subscription ID: {subscription_id}")
                # handle_invoice_payment_failed(event)
            elif event['type'] == 'customer.subscription.deleted':
                logger.info(f" Subscription cancelled. Subscription ID: {subscription_id}")
            #   handle_recurring_subscription_deleted(obj)
                logger.info(" Subscription cancelled. Subscription ID: {subscription_id}")
                # handle_subscription_deleted(event['data']['object'])
            elif event['type'] in [
                'invoice.created',
                'invoice.finalized',
                'invoice.updated',
                'charge.succeeded',
                'payment_intent.created'
            ]:
                logger.debug(f" Ignored event type (creation block): {event['type']}")
            else:
                logger.warning(f" Unhandled event type (creation block): {event['type']}")
        elif billing_reason == "subscription_cycle":
            logger.info(" Recurring subscription cycle payment.")
            logger.info(f" Subscription ID: {subscription_id}")
            handle_recurring_subscription_cycle(subscription_id, invoice_data, event["type"])
        elif billing_reason == "manual":
            logger.info(" Manual billing_reason - likely due to retry or missing payment method")
            handle_recurring_subscription_cycle(subscription_id, invoice_data, event["type"])  #  Treat same as recurring
        else:
            logger.warning(f" Unhandled billing_reason: {billing_reason}")
            # Optionally route by event["type"] below
        #🪝 Optional: Fallback to route other event types (safely)
        """
        if event['type'] == 'invoice.payment_failed':
            logger.info(" Subscription payment failed. Subscription ID: {subscription_id} ")
        #  handle_invoice_payment_failed(event)
        elif event['type'] == 'customer.subscription.deleted':
            logger.info(" Subscription cancelled. Subscription ID: {subscription_id}")
        # handle_subscription_deleted(event['data']['object'])
        elif event['type'] in [
            'invoice.created',
            'invoice.finalized',
            'invoice.updated',
            'charge.succeeded',
            'payment_intent.created'
        ]:
            logger.debug(f" Ignored event type: {event['type']}")
        else:
            logger.warning(f" Unhandled event type: {event['type']}")
        """
    except Exception as e:
        logger.exception(f" Exception while handling event: {event['type']}")
    return HttpResponse(status=200)
    #  ALWAYS return 200 OK so Stripe doesn't retry
    return HttpResponse(status=200)
