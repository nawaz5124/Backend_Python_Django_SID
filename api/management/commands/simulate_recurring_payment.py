#!/usr/bin/env python3
"""
Simulate a recurring monthly payment for a Stripe subscription.
Just update the subscription_id and customer_id as needed.
"""

import stripe
import os


# Stripe Test Secret Key (ENV or hardcoded)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Hard Coding - Replace with values from your DB or logs to test it 
subscription_id = "sub_1RlF361zwBHn0v2OsUGWgJf6"
customer_id = "cus_SgcHzjrfEO5NWh"

try:
    print(" Step 1: Creating a test invoice...")
    invoice = stripe.Invoice.create(
        customer=customer_id,
        subscription=subscription_id,
        auto_advance=True  # Automatically finalize after creation
    )
    print(f" Invoice created: {invoice.id}")

    print(" Step 2: Finalizing the invoice...")
    finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
    print(f"Finalized Invoice: {finalized_invoice.id} (Status: {finalized_invoice.status})")

    print("Step 3: Simulating payment...")
    paid_invoice = stripe.Invoice.pay(invoice.id)
    print(f"Invoice Paid Successfully! (Status: {paid_invoice.status})")

except Exception as e:
    print(f" Error occurred during simulation: {e}")