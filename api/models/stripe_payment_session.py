from django.db import models

class StripePaymentSessionView(models.Model):
    session_id = models.UUIDField(primary_key=True)
    donation_id = models.IntegerField(blank=True, null=True)
    payment_intent_id = models.CharField(max_length=100, unique=True)
    client_secret = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3)
    # New Fields for Subscription Support
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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'stripe_payment_session_view'
        managed = False  # Already exists in DB