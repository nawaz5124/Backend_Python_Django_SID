# api/utils/test_email_send.py

import os
import django

# Step 1: Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "donor_management.settings")
django.setup()

# Step 2: Correct import path (don't use `utils.`)
from api.utils.email_utils import send_donation_receipt

# Step 3: Test call
send_donation_receipt(
    to_email="nawaz5124@gmail.com",
    name="Nawaz",
    amount="£100",
    cause="Education Support",
    reference="CFT00901"
)

print(" Test email sent!")