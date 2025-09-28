from django.db.models import Max
from api.models.donors_model import DonorModel

def generate_cft_no():
    """
    Generates a sequential unique CFT number for new donors, starting from 001.
    """
    print("generate_cft_no() called.")  # Print for tracking
    last_cft_no = DonorModel.objects.aggregate(max_cft_no=Max("cft_no"))["max_cft_no"]
    print(f"Last CFT No from database: {last_cft_no}")

    if last_cft_no is None:  # If no donors exist in the database
        next_cft_no = 1
    else:
        next_cft_no = int(last_cft_no) + 1  # Increment the last CFT number

    formatted_cft_no = f"{next_cft_no:03d}"
    print(f"Generated new CFT No: {formatted_cft_no}")
    return formatted_cft_no