from api.models import DonationPayload, PaymentModel
from api.utils.formatters import format_diff_for_payload

def update_differences_in_payload(payment_ref):
    print(f" update_differences_in_payload() called for ref: {payment_ref}")
    try:
        # Step 1️: Get donation payload row
        payload = DonationPayload.objects.filter(payment_reference=payment_ref).first()
        if not payload or not payload.submitted_payload:
            print(" No payload or submitted_payload found.")
            return

        # Step 2️: Extract incoming (submitted form data)
        incoming = {
            **payload.submitted_payload.get("personalDetails", {}),
            **payload.submitted_payload.get("addressDetails", {})
        }

        # Step 3️: Navigate payment → donation → donor + address
        payment = PaymentModel.objects.select_related("donation__donor").filter(payment_reference=payment_ref).first()
        if not payment:
            print(" No PaymentModel found for reference.")
            return

        donation = payment.donation
        donor = donation.donor
        address = donation.addresses.first()  #  Uses related_name='addresses'

        if not address:
            print(" No AddressModel found for this donation.")
            return

        # Step 4️: Build 'existing' values from DB
        existing = {
            #  Donor fields
            "first_name": donor.first_name,
            "last_name": donor.last_name,
            "email": donor.email,
            "mobile": donor.mobile,
            "title": donor.title,
            "org_name": donor.org_name,
            #  Address fields
            "first_line": address.first_line,
            "street": address.street,
            "city": address.city,
            "county": address.county,
            "postcode": address.postcode,
        }

        # Step 5️: Generate diff
        diff_text = format_diff_for_payload(existing, incoming)

        # Step 6️: Save diff to DB
        payload.differences = diff_text
        payload.save(update_fields=["differences"])

        # Step 7️: Preview
        print("\n [DIFFERENCE PREVIEW]")
        print(diff_text or " No differences found.")

    except Exception as e:
        print(" Error during diff generation:", str(e))