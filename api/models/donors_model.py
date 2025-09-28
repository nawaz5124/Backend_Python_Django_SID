from django.db import models

class DonorModel(models.Model):
    cft_no = models.CharField(max_length=50, primary_key=True)  # Unique donor ID
    title = models.CharField(max_length=20, blank=True, null=True)  # Title (e.g., Mr., Ms.)
    first_name = models.CharField(max_length=100)  # First name
    last_name = models.CharField(max_length=100)  # Last name
    org_name = models.CharField(max_length=100, blank=True, null=True)  # Organization name
    email = models.EmailField(unique=True)  # Unique email
    mobile = models.CharField(max_length=15, blank=True, null=True)  # Mobile
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe ID
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe Subscription ID
    subscription_status = models.CharField(max_length=50, blank=True, null=True)  # Stripe subscription status (as-is)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when modified

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

