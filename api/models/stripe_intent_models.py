from django.db import models
import uuid

class StripeIntentModel(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation_id = models.IntegerField(null=True, blank=True)  # Link to your api_donationmodel if needed
    payment_intent_id = models.CharField(max_length=100, unique=True)  # Stripe Payment Intent ID
    client_secret = models.CharField(max_length=200)  # Client Secret from Stripe
    status = models.CharField(max_length=50, default="requires_payment_method")  # Payment status
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="GBP")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stripe_payment_session"
        verbose_name = "Stripe Payment Session"
        verbose_name_plural = "Stripe models"

    def __str__(self):
        return f"Session {self.session_id} - Intent: {self.payment_intent_id} - Status: {self.status}"  