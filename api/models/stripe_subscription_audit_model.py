from django.db import models
from datetime import datetime

class StripeSubscriptionAudit(models.Model):
    stripe_event_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_id = models.CharField(max_length=255)
    payment_intent_id = models.CharField(max_length=100, null=True, blank=True)
    price_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    interval = models.CharField(max_length=20, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    webhook_received_at = models.DateTimeField(auto_now_add=True)
    livemode = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')  # handled, failed, etc.
    notes = models.TextField(blank=True, null=True)
    raw_event_payload = models.JSONField(null=True, blank=True)  # Optional - for full debug
    plan_type = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    billing_reason = models.CharField(max_length=50, null=True, blank=True)
    collection_method = models.CharField(max_length=50, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    invoice_url = models.URLField(null=True, blank=True)
    invoice_status = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subscription_id} - {self.event_type} - {self.status}"