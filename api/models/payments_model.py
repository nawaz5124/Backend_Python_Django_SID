from django.db import models
from api.models.donations_model import DonationModel
from django.db.models import JSONField  

class PaymentModel(models.Model):
    payment_id = models.AutoField(primary_key=True)  # Unique Payment ID
    payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    donation = models.ForeignKey(DonationModel, on_delete=models.CASCADE, related_name="payments")  # Linked to Donation
    payment_mode = models.CharField(
        max_length=20,
        default="Card",  # Default payment mode
        verbose_name="Payment Mode"  # Field description
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True)
    currency = models.CharField(
        max_length=10,
        verbose_name="Payment Currency"
    )
    payment_reference = models.CharField(
        max_length=100,
        unique=True,  # Ensure reference is unique
        verbose_name="Payment Reference"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Transaction ID"  # Stripe/Payment Gateway transaction ID
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Completed", "Completed"), ("Failed", "Failed")],
        default="Pending",
        verbose_name="Payment Status"
    )
    # New Fields for Recurring/Subscription Payments
    stripe_subscription_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Stripe Subscription ID"
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name="Is Recurring?"
    )

    # New fields for Stripe invoice tracking
    stripe_invoice_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Stripe Invoice ID"
    )
    invoice_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Hosted Invoice URL"
    )
    billing_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Billing Reason (Stripe)"
    )
    subscription_status = models.CharField(
    max_length=50,
    null=True,
    blank=True,
    help_text="Latest status of the Stripe subscription"
    )
    stripe_customer_id = models.CharField(
    max_length=255, 
    null=True, blank=True)
    next_billing_date = models.DateTimeField(
    null=True,
    blank=True,
    help_text="Stripe current_period_end: Next scheduled billing date"  
    )   
    metadata_json = JSONField(
    null=True,
    blank=True,
    help_text="Optional metadata from Stripe for campaign tracking or internal notes"
    )
    stripe_invoice_id = models.CharField(max_length=64, blank=True, null=True, unique=True)  # unique for idempotency
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")  # Timestamp when created
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")  # Timestamp when modified

    def __str__(self):
        return f"Payment {self.payment_id} for Donation {self.donation.donation_id}"
#
# Alias for compatibility with views expecting ApiPaymentModel
ApiPaymentModel = PaymentModel