from decimal import Decimal
from api.models.donation_payload_model import DonationPayload
from api.models import PaymentModel, StripePaymentSessionView  # Only what's required
from api.utils.donation_payload_diff_updater import update_differences_in_payload  #  Import at the top
from api.utils.donation_payload_diff_updater import update_differences_in_payload  #  Import at the top


# Step 1: Log incoming payload
def log_donation_payload(data, ip=None, user_agent=None):
    try:
        print(" log_donation_payload() triggered")
        DonationPayload.objects.create(
            #  Traceability
            donation_id=None,
            cft_no=None,
            receipt_generated=False,
            donation_status="received",
            differences=None,

            #  paymentPlanDetails
            donation_frequency=data.get("paymentPlanDetails", {}).get("donationFrequency"),
            payment_reference=data.get("paymentDetails", {}).get("paymentReference"),

            #  personalDetails
            title=data.get("personalDetails", {}).get("title"),
            first_name=data.get("personalDetails", {}).get("firstName"),
            last_name=data.get("personalDetails", {}).get("lastName"),
            email=data.get("personalDetails", {}).get("email"),
            mobile=data.get("personalDetails", {}).get("mobile"),
            org_name=data.get("personalDetails", {}).get("orgName"),
            stripe_customer_id=data.get("personalDetails", {}).get("stripeCustomerId"),

            #  addressDetails
            first_line=data.get("addressDetails", {}).get("firstLine"),
            street=data.get("addressDetails", {}).get("street"),
            city=data.get("addressDetails", {}).get("city"),
            county=data.get("addressDetails", {}).get("county"),
            postcode=data.get("addressDetails", {}).get("postcode"),

            #  donationDetails
            fund=data.get("donationDetails", {}).get("fund"),
            cause=data.get("donationDetails", {}).get("cause"),
            amount=Decimal(data.get("donationDetails", {}).get("amount", "0.00")),
            gdpr_consent=data.get("donationDetails", {}).get("gdprConsent", False),
            cft_fund_consent=data.get("donationDetails", {}).get("cftFundConsent", False),
            gift_aid_consent=data.get("donationDetails", {}).get("giftAidConsent", False),

            #  paymentDetails
            paymentMode=data.get("paymentDetails", {}).get("paymentMode"),
            currency=data.get("paymentDetails", {}).get("currency"),
            transaction_id=data.get("paymentDetails", {}).get("transactionId"),

            #  Meta
            submitted_payload=data,
        )
    except Exception as e:
        print(" Error logging payload:", str(e))


# Step 2: Update the record once donation is fully processed
# api/utils/donation_payload_logger.py

from api.models import DonationPayload, PaymentModel

def update_logged_payload_from_donation(payment_ref):
    print(f" update_logged_payload_from_donation() called for ref: {payment_ref}")
    try:
        # Step 1️: Fetch the payment
        payment_record = PaymentModel.objects.filter(payment_reference=payment_ref).first()
        if not payment_record:
            print(f" No PaymentModel found for reference: {payment_ref}")
            return

        # Step 2️: Navigate to related donor and donation
        donation_record = payment_record.donation
        donor_record = donation_record.donor

        # Step 3️: Get donation status directly from donation table
        donation_status = donation_record.donation_status  #  final, post-webhook value

        # Step 4️: Preview update
        print(" [Payload Update Preview]")
        print(f" donation_id: {donation_record.donation_id}")
        print(f" cft_no: {donor_record.cft_no}")
        print(f" donation_status: {donation_status}")

        # Step 5️: Apply update to DonationPayload table
        updated_count = DonationPayload.objects.filter(payment_reference=payment_ref).update(
            donation_id=donation_record.donation_id,
            cft_no=donor_record.cft_no,
            donation_status=donation_status,
            stripe_customer_id="NA",            # No customer tracking for one-off
            stripe_subscription_id="NA",        # Not a subscription
            transaction_id=payment_record.transaction_id,
            payment_intent_id=payment_record.payment_intent_id
            
        )
        #  Optional preview step at the bottom
        update_differences_in_payload(payment_ref)
        
        # Step 6️: Confirm update
        if updated_count:
            print(f" DonationPayload updated in DB for reference: {payment_ref}")
        else:
            print(f" No matching DonationPayload found for reference: {payment_ref}")

    except Exception as e:
        print(" Error updating DonationPayload:", str(e))