

from django.db import models

# Define fund choices
fund_choices = [
    ("zakaath", "Zakaath"),
    ("sadaqah", "Sadaqah"),
    ("lillah", "Lillah"),
    ("other", "Other"),
]
    
# Define cause choices
cause_choices = [
    ("building_institutions", "Building of Institutions"),
    ("sponsoring_child", "Sponsoring a Child"),
    ("where_needed", "Where Most Needed"),
]

class DonationModel(models.Model):
    donation_id = models.AutoField(primary_key=True)
    donor = models.ForeignKey("DonorModel", on_delete=models.CASCADE)

    # Mandatory fields for fund and cause
    donation_type = models.CharField(
        max_length=50,
        choices=fund_choices,
        null=False,  # Cannot be null
        blank=False,  # Cannot be blank
    )
    donation_cause = models.CharField(
        max_length=255,
        choices=cause_choices,
        null=False,  # Cannot be null
        blank=False,  # Cannot be blank
    )

    # Other fields remain unchanged
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gdpr_consent = models.BooleanField(default=False)  # GDPR consent
    cft_fund_consent = models.BooleanField(default=False)  # CFT Fund consent
    gift_aid_consent = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    donation_frequency = models.CharField(max_length=20, blank=True, null=True, default="One-Off")
    receipt_generated = models.BooleanField(default=False)
    donation_status = models.CharField(max_length=20, default="Pending")
    # New Field for Recurring Support
    stripe_subscription_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Stripe Subscription ID"
    )
    subscription_status = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Stripe Subscription Status",
    )
    stripe_invoice_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Donation {self.donation_id} by {self.donor.first_name} {self.donor.last_name}"
    

ApiDonationModel = DonationModel