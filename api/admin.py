from django.contrib import admin
from api.models.donors_model import DonorModel
from api.models.address_model import AddressModel
from api.models.donations_model import DonationModel
# from api.models.giftaid_model import GiftAidModel
from api.models.payments_model import PaymentModel
from api.models.stripe_intent_models import StripeIntentModel  #  Added new import


# Donor Admin
@admin.register(DonorModel)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("cft_no", "first_name", "last_name", "email", "mobile", "created_at")  # Display key donor details
    search_fields = ("cft_no", "email", "mobile")  # Enable search by critical fields
    list_filter = ("created_at",)  # Filter by creation date


# Donation Admin
@admin.register(DonationModel)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donation_id", "payment_intent_id", "donor", "donation_type", "donation_cause", "amount", "created_at")  # Ensure payment_frequency is included
    search_fields = ("donation_id", "donor__first_name", "donor__last_name", "cause")  # Enable search by donation details
    list_filter = ("donation_type", "donation_cause")  # Filter by donation type and frequency


# Payment Admin
@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "transaction_id", "payment_reference", "payment_mode", "payment_status", "created_at", "donation")  # Include status for clarity
    search_fields = ("payment_reference", "transaction_id", "donation__donation_id")  # Ensure search by related donation
    list_filter = ("payment_mode", "payment_status", "currency")  # Filter by payment mode, status, and currency


# Address Admin
@admin.register(AddressModel)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("donor", "first_line", "street", "city", "county", "postcode", "created_at")
    search_fields = ("donor__first_name", "donor__last_name", "postcode")
    list_filter = ("city", "county")


#  New: Stripe Intent Admin
@admin.register(StripeIntentModel)
class StripeIntentAdmin(admin.ModelAdmin):
    list_display = ("payment_intent_id", "status", "created_at", "updated_at")  # Key fields to display
    search_fields = ("payment_intent_id", "status")  # Quick search by intent ID or status
    list_filter = ("status", "created_at")  # Filter by status and creation date