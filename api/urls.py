from django.urls import path
from api.views.donors_view import DonorAPIView, DonorListAPIView
from api.views.donors import DonorsAPIView
from api.views.donors_test_view import get_donors_test
from api.views.address_views import address_lookup
from api.views.api_overview import api_overview
from api.views.stripe_views import StripePaymentIntentAPIView
from api.views.webhooks import stripe_webhook
from api.views.donation_create_api_view import create_donation_api
from api.views.donation_choices_api_view import get_donation_choices
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views.api_auth_service_view import (internal_token_view,refresh_service_token, get_service_token, logout,debug_token_view, my_protected_view)  #  Fixed Import
# from api.views.auth_cookie_views import (logout)
from api.views.test_cookie_view import test_cookie, check_cookie
from api.views.donation_payload_view import DonationPayloadView
from api.views.email_api_view import send_email_view
from .views import frontend_logger_view
from api.views.stripe_subscription_monthly_api_view import subscription_intent_view
from api.views.stripe_subscription_webhook_view import stripe_subscription_webhook
from api.views.stripe_subscription_attach_payment_method_view import attach_payment_method_view

# Define urlpatterns
urlpatterns = [
    # General API Overview
    path("", api_overview, name="api-overview"),

    # Donors API
    path("donors/", DonorsAPIView.as_view(), name="donors-api"),
    path("donors-test/", get_donors_test, name="get-donors-test"),
    path("donors/create/", DonorAPIView.as_view(), name="donor-create"),
    path("donors/<str:pk>/", DonorAPIView.as_view(), name="donor-update"),
    path("donors/list/", DonorListAPIView.as_view(), name="donor-list"),

    # Address Lookup
    path("address/lookup/", address_lookup, name="address-lookup"),

    # Donations API
    path("donations/create/", create_donation_api, name="create-donation"),
    path("donations/choices/", get_donation_choices, name="get-donation-choices"),
    path('donations/payload/', DonationPayloadView.as_view(), name='donation-payload'),

    # Stripe Payment-Intent API
    path("stripe/payment-intent/", StripePaymentIntentAPIView.as_view(), name="stripe-payment-intent"),
    #path('stripe/payment-intent/', StripePaymentIntentView.as_view(), name='stripe-payment-intent'),
    path('stripe/subscription-intent/', subscription_intent_view, name='subscription-intent'),
    path("stripe/attach-payment-method/", attach_payment_method_view, name="attach_payment_method"),

    # Webhooks
    # path("webhook/", stripe_webhook, name="stripe-webhook"),
    # path("webhook/", stripe_webhook, name="stripe-webhook"),
    path('stripe/one-off-webhook/', stripe_webhook, name='stripe_one_off_webhook'),
    path('stripe/subscription-webhook/', stripe_subscription_webhook, name='stripe_subscription_webhook'),
    

    # Email API
    path("send-email/", send_email_view, name="send_email"),
    

    # JWT Authentication Endpoints (FIXED)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # Get Access & Refresh Token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh Access Token

    path("auth/internal-token/", internal_token_view, name="internal-jwt-token"),  #  Fixed Import
    path("auth/service-token/", get_service_token, name="service-token"),  #  Added this for frontend
    path("auth/logout/", logout, name="logout"),  #  Logout API (clears cookies)
    path("auth/refresh-token/", refresh_service_token, name="refresh-token"),  #  New Refresh Token API
    path("auth/debug-token/", debug_token_view, name="debug-token"),  #  Debugging Route

    #  Include Test Cookie Endpoints (Fixed API Path Consistency)
    path("test-cookie/", test_cookie, name="test-cookie"),
    path("check-cookie/", check_cookie, name="check-cookie"),
    path("auth/test-cookie-token/", my_protected_view, name="test-cookie-token"),

    # Frontend Logger View
    path("frontend-log/", frontend_logger_view.frontend_log_receiver, name="frontend_log"),    

]