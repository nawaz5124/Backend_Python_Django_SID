from api.models import DonationModel, PaymentModel, DonorModel
from django.utils.timezone import now
import logging
import json
import stripe
from datetime import datetime
from django.utils.timezone import make_aware


logger = logging.getLogger(__name__)

def backfill_recurring_donation_and_payment(event: dict, status: str = "Pending"):
    logger.info("[Recurring] Backfill donation and payment records for invoice event")

    # Accept either full Stripe event or raw invoice payload
    invoice = event if "billing_reason" in event else event.get("data", {}).get("object", {})
    subscription_id = invoice.get("subscription")
    logger.info(f" Subscription ID TEST: {subscription_id}")
    
    try:
        #subscription_id = invoice.get("subscription")
        payment_intent_id = invoice.get("payment_intent")
        amount = invoice.get("amount_due") or invoice.get("amount_paid")
        logger.info(f" Amount: {amount} (in cents)")
        currency = invoice.get("currency", "GBP")
        invoice_url = invoice.get("hosted_invoice_url")
        stripe_customer_id = invoice.get("customer")
        logger.info(f" Stripe Customer ID: {stripe_customer_id}")
        invoice_id = invoice.get("id")
        billing_reason = invoice.get("billing_reason", "N/A")
        stripe_customer_id = invoice.get('customer')                     # stripe_customer_id
        #subscription_id = invoice.get('subscription')                    # stripe_subscription_id
        invoice_id = invoice.get('id')                                   # stripe_invoice_id
        payment_intent_id = invoice.get('payment_intent')                # payment_intent_id / transaction_id
        status = invoice.get('status') or "paid"                         # payment_status
        amount = invoice.get('amount_paid')                              # amount (in cents)
        currency = invoice.get('currency')                               # currency
        invoice_url = invoice.get('hosted_invoice_url') or "N/A"         # invoice_url
        billing_reason = invoice.get('billing_reason') or "N/A"          # billing_reason
        amount_in_major_unit = amount / 100  # Convert cents to major unit (e.g. GBP)

        #  Extract customer ID from Stripe payload
        stripe_customer_id = event.get("customer")
        if not stripe_customer_id:
            logger.error(" Stripe customer ID missing in payload.")
            return

        #  Dynamically fetch the correct donor using stripe_customer_id
        donor = DonorModel.objects.get(stripe_customer_id=stripe_customer_id)
        logger.info(f" Donor found: {donor.first_name} {donor.last_name} (CFT No: {donor.cft_no})")
        #  Backfill DonationModel
        
        logger.info(f" Payload Extracted:\n"
                     f" Invoice ID: {invoice_id}\n"
                     f" Payment Intent ID: {payment_intent_id}\n"
                     f" Customer ID: {stripe_customer_id}\n"
                     f" Subscription ID: {subscription_id}\n"
                     f" Amount: {amount_in_major_unit:.2f} {currency.upper()}\n"
                     f" Invoice URL: {invoice_url}\n"
                     f" Billing Reason: {billing_reason}")        
        # Find the first/original donation with same subscription ID
        original_donation = DonationModel.objects.filter(stripe_subscription_id=subscription_id).order_by("created_at").first()
        logger.info(f" Original Donation: {original_donation.donation_id if original_donation else 'None'}")
        donation = DonationModel.objects.create(
            donor=donor,  # Assuming donor ID is 53 for backfill
            donation_type=original_donation.donation_type,
            donation_cause=original_donation.donation_cause,
            amount=amount / 100 if amount else 0,
            donation_status=status,
            donation_frequency="Recurring",
            payment_intent_id=payment_intent_id,
            stripe_subscription_id=subscription_id,
            subscription_status=status,
            created_at=now(),
            updated_at=now()
        )
        logger.info(f" Reusing donation_type={original_donation.donation_type}, cause={original_donation.donation_cause} from original donation ID={original_donation.donation_id}")
        logger.info(f" Donation record created with ID: {donation.donation_id}")

     #   invoice = event
     #   stripe_customer_id = invoice.get('customer')                     # stripe_customer_id
     #   subscription_id = invoice.get('subscription')                    # stripe_subscription_id
     #   invoice_id = invoice.get('id')                                   # stripe_invoice_id
     #   payment_intent_id = invoice.get('payment_intent')                # payment_intent_id / transaction_id
     #   status = invoice.get('status') or "paid"                         # payment_status
     #   amount = invoice.get('amount_paid')                              # amount (in cents)
     #   currency = invoice.get('currency')                               # currency
     #   invoice_url = invoice.get('hosted_invoice_url') or "N/A"         # invoice_url
     #   billing_reason = invoice.get('billing_reason') or "N/A"          # billing_reason
        # Fetch subscription object from Stripe
        subscription_obj = stripe.Subscription.retrieve(subscription_id)
        subscription_status = subscription_obj.get("status", "unknown")  # active, canceled, etc.  
        logger.info(f" Subscription Metadata Before: {subscription_obj.metadata}") 
        #  This is also good — metadata is a StripeObject too
        logger.info(f" Subscription Metadata Before: {subscription_obj.metadata}")

        # Convert metadata to plain dict
        metadata_dict = dict(subscription_obj.metadata) if subscription_obj.metadata else {}
        metadata_json = json.dumps(metadata_dict, indent=2, ensure_ascii=False)

        logger.info(f" Subscription Metadata After: {metadata_json}")
        logger.info(f" Subscription Metadata After: {subscription_obj.metadata}")
        period_end_unix = subscription_obj.get("current_period_end", 0)
        next_billing_date = make_aware(datetime.fromtimestamp(period_end_unix)) if period_end_unix else None
        charge_id = invoice.get("charge")  # this is the true transaction ID transaction_id=invoice.get("charge")  # direct and clean

        #  Backfill PaymentModel
        existing_payment = PaymentModel.objects.filter(payment_reference=payment_intent_id).first()

        if existing_payment:
            logger.warning(f"[Backfill] Payment already exists for reference: {payment_intent_id}")
            payment = existing_payment  # Optional: reuse it if needed
        else:
            payment = PaymentModel.objects.create(
                donation=donation,
                transaction_id=charge_id,  # Use charge ID as transaction ID
                payment_intent_id=payment_intent_id,
                payment_reference=payment_intent_id, # for recurring billing, the same subscription_id is reused for every monthly invoice/payment. 
                payment_status=status,  # e.g. "Paid"
                amount=amount / 100 if amount else 0,
                currency=currency.upper() if currency else "GBP",
                payment_mode="Card",
                invoice_url=invoice_url,
                is_recurring=True,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=subscription_id,
                stripe_invoice_id=invoice_id,
                billing_reason=billing_reason,
                subscription_status=subscription_status,
                next_billing_date=next_billing_date,
                metadata_json=metadata_json,
                created_at=now(),
                updated_at=now()
                )
            logger.info(f" Payment record created with ID: {payment.payment_id}")



    except Exception as e:
        logger.exception(f" Backfill failed: {str(e)}")