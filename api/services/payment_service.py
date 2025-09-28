from api.models.payments_model import PaymentModel
from api.exceptions import ValidationError, BaseAPIException
import logging
from django.utils import timezone

from api.models.donation_payload_model import DonationPayload
from django.utils.timezone import now
from django.utils.timezone import make_aware
import json
from datetime import datetime
from api.models.stripe_intent_models import StripeIntentModel
import stripe
from django.conf import settings

logger = logging.getLogger(__name__)

def process_payment(donation, payment_details):
    """
    Create a payment entry in the database.
    Checks for duplicate payment_reference before creating a new payment.
    """
    logger.info(f"INFO: [Payment Service] - Starting process_payment")
    logger.debug(f"DEBUG: [Payment Service] - process_payment called with donation: {donation} and payment_details: {payment_details}")

    try:
        # Extract payment reference
        payment_reference = payment_details["paymentReference"]
        logger.info(f"INFO: [Payment Service] - Processing payment with reference: {payment_reference}")

        # Check for duplicate payment_reference
        if PaymentModel.objects.filter(payment_reference=payment_reference).exists():
            logger.error(f"ERROR: [Payment Service] - Duplicate payment_reference found: {payment_reference}")
            raise ValidationError(f"Duplicate payment_reference: {payment_reference}")

        # Detect monthly subscription
        is_subscription = payment_reference.startswith("sub_")

        # Create a new payment record
        payment = PaymentModel.objects.create(
            donation=donation,
            payment_mode=payment_details["paymentMode"],
            currency=payment_details["currency"],            
            payment_reference=payment_reference,
            #payment_intent_id=payment_reference,
            transaction_id=payment_details.get("transactionId", None),
            payment_status="Pending",  # Default status
            stripe_subscription_id=payment_reference if is_subscription else None,
            is_recurring=is_subscription,
        )

        logger.info(f"INFO: [Payment Service] - Stripe Payment created successfully: {payment}")
        return payment

    except ValidationError as ve:
        logger.error(f"ERROR: [Payment Service] - Validation Error in process_payment: {str(ve)}")
        raise ve

    except Exception as e:
        logger.error(f"ERROR: [Payment Service] - An error occurred in process_payment: {str(e)}")
        raise BaseAPIException(f"An error occurred while processing the payment: {str(e)}")

def update_payment_from_subscription_webhook(subscription_id, invoice_data):
    logger.info(f" [Payment Service] Updating PaymentModel from invoice.paid webhook | subscription_id: {subscription_id}")

    payment = PaymentModel.objects.filter(stripe_subscription_id=subscription_id).first()
    if not payment:
        logger.warning(f" [Payment Service] No PaymentModel found for subscription_id: {subscription_id}")
        return

    # Basic updates
    payment.stripe_invoice_id = invoice_data.get("id")
    payment.invoice_url = invoice_data.get("hosted_invoice_url")
    payment.billing_reason = invoice_data.get("billing_reason")
    #payment.subscription_status = invoice_data.get("status", "active")
    try:
        subscription_id = invoice_data.get("subscription")
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Must be set in your Django settings

        if subscription_id:
            subscription_obj = stripe.Subscription.retrieve(subscription_id)
            subscription_status = subscription_obj.get("status", "unknown")  # active, canceled, etc.
            payment.subscription_status = subscription_status
            logger.info(f" Fetched subscription status from Stripe: {subscription_status}")
        else:
            logger.warning(" No subscription_id found in invoice_data.")
            payment.subscription_status = "unknown"

    except Exception as e:
        logger.warning(f" Failed to fetch subscription status from Stripe: {str(e)}")
        payment.subscription_status = "error_fetching"
    
    payment.payment_status = invoice_data.get("status")
    payment.payment_intent_id = invoice_data.get("payment_intent")
    payment.is_recurring = True
    payment.updated_at = timezone.now()

    # Enrich PaymentModel
    try:
        period_end_unix = invoice_data.get("lines", {}).get("data", [])[0].get("period", {}).get("end")
        if period_end_unix:
            payment.next_billing_date = make_aware(datetime.fromtimestamp(period_end_unix))
            logger.info(f" next_billing_date set to: {payment.next_billing_date}")

        # Map more values
        payment.transaction_id = invoice_data.get("charge")
        payment.stripe_customer_id = invoice_data.get("customer")
        payment.metadata_json = json.dumps(invoice_data, indent=2, ensure_ascii=False)
        payment.amount = invoice_data.get("amount_paid") / 100  # Convert pence to pounds
        payment.save()
        logger.info(f" PaymentModel enriched with metadata and next billing info")

    except Exception as e:
        logger.warning(f" Error enriching PaymentModel: {str(e)}")

    # Update DonationPayload if found
    #payload = DonationPayload.objects.filter(payment_reference=payment.payment_reference).first()
    payload = DonationPayload.objects.filter(payment_reference=invoice_data.get("subscription")).first()
    if payload:
        #payload.donation_status = "Completed"
        payload.donation_status = invoice_data.get("status")
        payload.stripe_customer_id = invoice_data.get("customer")
        payload.transaction_id = invoice_data.get("charge")
        payload.stripe_subscription_id = subscription_id
        payload.payment_intent_id = invoice_data.get("payment_intent")
        payload.save()
        logger.info(f" DonationPayload updated for ref: {payment.payment_reference}")
    else:
        logger.warning(f" No DonationPayload found for ref: {payment.payment_reference}")

    logger.info(f" [Payment Service] PaymentModel updated successfully for subscription_id: {subscription_id}")

    payment = PaymentModel.objects.filter(stripe_subscription_id=subscription_id).first()
    if not payment:
        logger.warning(f" [Payment Service] No PaymentModel found for subscription_id: {subscription_id}")
        return
  
    # Step: Update DonationModel fields (related to subscription)
    try:
        donation = payment.donation
        if donation:
            donation.donation_status = invoice_data.get("status")  # or dynamic if you prefer
            donation.stripe_subscription_id = subscription_id
            logger.info(f" Updating DonationModel with stripe_subscription_id: {subscription_id}")
            donation.subscription_status = subscription_status
            logger.info(f" Updating DonationModel with subscription status: {subscription_status}")
            #payment.subscription_status = subscription_status
            donation.updated_at = timezone.now()
            donation.save()
            logger.info(f" DonationModel updated for subscription_id: {subscription_id}")
        else:
            logger.warning(" No DonationModel found for payment.")
    except Exception as e:
        logger.warning(f" Error updating DonationModel fields: {str(e)}")

# 🧾 Step Z: Update StripePaymentSession
    try:
        payment_intent = invoice_data.get("payment_intent")
        #logger.info(f" [Payment Service] Raw invoice_data: {invoice_data}")
        logger.info(f" [Payment Service] Raw invoice_data: ")
        logger.info(f" [Payment Service] Attempting to update session for payment_intent: {payment_intent}")

        if payment_intent:
            stripe_session = StripeIntentModel.objects.filter(payment_intent_id=payment_intent).first()
            logger.info(f" [Payment Service] Found StripePaymentSession: {stripe_session}")
            
            if stripe_session:
                stripe_session.donation_id = payment.donation_id
                stripe_session.status = invoice_data.get("status", "paid")  # fallback to 'paid'
                stripe_session.updated_at = timezone.now()
                stripe_session.save()
                logger.info(f" StripePaymentSession updated successfully.")
            else:
                logger.warning(f" No StripePaymentSession found for payment_intent: {payment_intent}")
        else:
            logger.warning(" No payment_intent found in invoice_data.")

    except Exception as e:
        logger.error(f" Error updating StripePaymentSession: {str(e)}")

    #  Step: Update DonorModel with Stripe Subscription Info
    try:
        donor = payment.donation.donor
        logger.info(f" [Payment Service] Updating DonorModel for CFT No: {donor.cft_no} with subscription_id: {subscription_id}")
        if donor:
            updated = False

            # Subscription ID
            if not donor.stripe_subscription_id or donor.stripe_subscription_id != subscription_id:
                donor.stripe_subscription_id = subscription_id
                updated = True

            # Subscription Status
            if not donor.subscription_status or donor.subscription_status != subscription_status:
                donor.subscription_status = subscription_status
                updated = True

            # Stripe Customer ID
            invoice_customer_id = invoice_data.get("customer")
            if invoice_customer_id and (not donor.stripe_customer_id or donor.stripe_customer_id != invoice_customer_id):
                donor.stripe_customer_id = invoice_customer_id
                updated = True

            if updated:
                donor.save()
                logger.info(f" DonorModel updated with subscription_id, status, and customer_id for CFT No: {donor.cft_no}")
            else:
                logger.info(f" DonorModel already has correct subscription info. No update needed.")

        else:
            logger.warning(" No DonorModel found for this donation/payment.")

    except Exception as e:
        logger.error(f" Error updating DonorModel: {str(e)}")