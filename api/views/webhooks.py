import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from api.models.payments_model import ApiPaymentModel
from api.models.donations_model import ApiDonationModel
from api.models.stripe_intent_models import StripeIntentModel
import json

#  Import our payload update function
from api.utils.donation_payload_logger import update_logged_payload_from_donation

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    logging.info(f"[One-Off Webhook] - Received payload: {payload[:100]}...")  # Log first 100 chars for brevity
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    #  Step 1: Verify the Stripe event
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        logger.info(f"[One-Off Webhook] - Received event: {event['type']}")
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"[One-Off Webhook] - Invalid payload or signature: {e}")
        return HttpResponse(status=400)

    # 🎯 Step 1.5: Filter out subscription payments
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        invoice_id = intent.get("invoice")  # This field exists for subscription payments
        customer_id = intent.get("customer")
        payment_intent_id = intent.get("id")
        
        if invoice_id:
            logger.info(f"[One-Off Webhook] - 🔄 SUBSCRIPTION PAYMENT DETECTED:")
            logger.info(f"[One-Off Webhook] - 📋 Payment Intent: {payment_intent_id}")
            logger.info(f"[One-Off Webhook] - 🧾 Invoice: {invoice_id}")
            logger.info(f"[One-Off Webhook] - 👤 Customer: {customer_id}")
            logger.info(f"[One-Off Webhook] - ✅ Ignoring - will be handled by subscription webhook")
            return HttpResponse(status=200)
        else:
            logger.info(f"[One-Off Webhook] - ✅ TRUE ONE-OFF PAYMENT DETECTED")
            logger.info(f"[One-Off Webhook] - 📋 Payment Intent: {payment_intent_id}")
            logger.info(f"[One-Off Webhook] - 🔄 Processing as one-off payment...")

    #  Step 2: Handle payment success (only true one-off payments reach here)
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        payment_intent_id = intent.get("id")
        charge_id = intent.get("latest_charge")
        
        logger.info(f"[One-Off Webhook] - Processing one-off PaymentIntent: {payment_intent_id}")
        logger.info(f"[One-Off Webhook] - Charge ID: {charge_id}")

        if not charge_id:
            logger.warning(f"[One-Off Webhook] - No latest_charge found for PaymentIntent: {payment_intent_id}")

        try:
            #  2.1 Update Stripe Session
            session = StripeIntentModel.objects.get(payment_intent_id=payment_intent_id)
            session.status = intent.get("status", "unknown")  # dynamic assignment
            donation = ApiDonationModel.objects.get(payment_intent_id=payment_intent_id)
            session.donation_id = donation.donation_id
            session.save(update_fields=["status", "donation_id"])
            logger.info(f"[One-Off Webhook] - StripeIntent updated with donation_id={donation.donation_id}")
        except StripeIntentModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - StripeIntent not found for PaymentIntent {payment_intent_id}")
        except ApiDonationModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - Donation not found for PaymentIntent {payment_intent_id}")
        except Exception as e:
            logger.exception(f"[One-Off Webhook] - Error updating Stripe session: {e}")
            return HttpResponse(status=500)

        try:
            #  2.2 Update Donation status
            donation = ApiDonationModel.objects.get(payment_intent_id=payment_intent_id)
            stripe_status = intent.get("status", "unknown")
            donation.donation_status = stripe_status
            donation.stripe_subscription_id = "NA"  # One-off payment, no subscription involved
            donation.subscription_status = "NA"  # No subscription status for one-off payments
            donation.save(update_fields=["donation_status","stripe_subscription_id","subscription_status"])
            logger.info(f"[One-Off Webhook] - Donation {donation.donation_id} updated to status: {stripe_status}")
        except ApiDonationModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - Donation not found for PaymentIntent {payment_intent_id}")

        try:
            # 2.3 Update Payment status
            payment = ApiPaymentModel.objects.get(payment_reference=payment_intent_id)
            stripe_status = intent.get("status", "unknown")
            payment.payment_status = stripe_status
            payment.transaction_id = charge_id
            payment.payment_intent_id = payment_intent_id
            payment.amount = intent.get("amount_received", 0) / 100.0  # Convert cents to major currency unit
            payment.metadata_json = intent.to_dict()  # Save Stripe metadata
            payment.next_billing_date = None  # One-off payment, no next billing date
            payment.subscription_status = "NA"  # No subscription status for one-off payments
            payment.stripe_subscription_id = "NA"  # No subscription involved
            payment.stripe_invoice_id = None  # No invoice for one-off payments (NULL instead of "NA")
            payment.billing_reason = "one-off"  # Set billing reason for one-off payments
            payment.invoice_url = "NA"  # No invoice URL for one-off payments
            payment.save(update_fields=["payment_status", "transaction_id", "payment_intent_id","amount","metadata_json","billing_reason","subscription_status","stripe_subscription_id","invoice_url"])
            logger.info(f"[One-Off Webhook] - Payment {payment.payment_id} updated: {stripe_status}, Amount: £{payment.amount}")
        except ApiPaymentModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - Payment not found for reference {payment_intent_id}")      
        except Exception as e:
            logger.exception(f"[One-Off Webhook] - Error syncing payment: {e}")
            return HttpResponse(status=500)

        try:
            # 2.4 Update our audit table (api_donationpayload)
            update_logged_payload_from_donation(payment_intent_id)
            logger.info(f"[One-Off Webhook] - DonationPayload updated via logger for {payment_intent_id}")
        except Exception as e:
            logger.warning(f"[One-Off Webhook] - Could not update DonationPayload for {payment_intent_id}: {e}")

    # Step 3: Handle payment failure (only true one-off failures reach here)
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        payment_intent_id = intent.get("id")
        
        logger.error(f"[One-Off Webhook] - One-off PaymentIntent FAILED: {payment_intent_id}")

        # 🎯 Double-check: Filter subscription payment failures (safety check)
        invoice_id = intent.get("invoice")
        if invoice_id:
            logger.warning(f"[One-Off Webhook] - 🔄 SUBSCRIPTION PAYMENT FAILURE DETECTED:")
            logger.warning(f"[One-Off Webhook] - 📋 Payment Intent: {payment_intent_id}")
            logger.warning(f"[One-Off Webhook] - 🧾 Invoice: {invoice_id}")
            logger.warning(f"[One-Off Webhook] - ✅ Ignoring - will be handled by subscription webhook")
            return HttpResponse(status=200)

        try:
            #  3.1 Mark Donation as failed
            donation = ApiDonationModel.objects.get(payment_intent_id=payment_intent_id)
            donation.donation_status = "failed"
            donation.save(update_fields=["donation_status"])
            logger.info(f"[One-Off Webhook] - Marked donation {donation.donation_id} as failed")
        except ApiDonationModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - Donation not found for failed intent {payment_intent_id}")

        try:
            #  3.2 Mark Payment as failed
            payment = ApiPaymentModel.objects.get(payment_reference=payment_intent_id)
            payment.payment_status = "failed"
            payment.save(update_fields=["payment_status"])
            logger.info(f"[One-Off Webhook] - Marked payment {payment.payment_id} as failed")
        except ApiPaymentModel.DoesNotExist:
            logger.warning(f"[One-Off Webhook] - Payment not found for failed intent {payment_intent_id}")
        except Exception as e:
            logger.exception(f"[One-Off Webhook] - Error marking payment as failed: {e}")
            return HttpResponse(status=500)

    # Step 4: Catch-all for unhandled events
    else:
        logger.info(f"[One-Off Webhook] 🔁 Event {event['type']} received but not handled.")

    return HttpResponse(status=200)