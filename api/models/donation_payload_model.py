from django.db import models


class DonationPayload(models.Model):
    #  Traceability

    donation_id = models.IntegerField(null=True, blank=True)
    cft_no = models.CharField(max_length=50, null=True, blank=True)

    receipt_generated = models.BooleanField(default=False)
    donation_status = models.CharField(max_length=50, default="received")
    differences = models.TextField(null=True, blank=True)

    #  paymentPlanDetails
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    donation_frequency = models.CharField(max_length=20, blank=True, null=True, default="One-Off")

    # personalDetails
    title = models.CharField(max_length=20, blank=True, null=True)  # Title (e.g., Mr., Ms.)
    first_name = models.CharField(max_length=100)  # First name
    last_name = models.CharField(max_length=100)  # Last name
    org_name = models.CharField(max_length=100, blank=True, null=True)  # Organization name
    email = models.EmailField() #  Correct — no constraint
    mobile = models.CharField(max_length=15, blank=True, null=True)  # Mobile
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe ID
    stripe_subscription_id = models.CharField(max_length=150,blank=True,null=True,verbose_name="Stripe Subscription ID")

    #  addressDetails
    first_line = models.CharField(max_length=255, blank=True, null=True)  # Address line 1
    street = models.CharField(max_length=255, blank=True, null=True)  # Street name
    city = models.CharField(max_length=100, blank=True, null=True)  # City
    county = models.CharField(max_length=100, blank=True, null=True)  # County
    postcode = models.CharField(max_length=20, blank=True, null=True)  # Postcode

    #  donationDetails
    fund = models.CharField(max_length=50, null=True, blank=True)
    cause = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gdpr_consent = models.BooleanField(default=False)  # GDPR consent
    cft_fund_consent = models.BooleanField(default=False)  # CFT Fund consent
    gift_aid_consent = models.BooleanField(default=False) # Gift Aid consent

    #  paymentDetails
    paymentMode = models.CharField(max_length=20, null=True, blank=True)
    currency = models.CharField(max_length=10, default='GBP')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    #  Meta
    submitted_payload = models.JSONField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payload from {self.email} at {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"