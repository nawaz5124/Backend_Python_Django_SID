from django.http import JsonResponse

from api.models.donor_test_model import DonorTest  # If DonorTest exists here


def get_donors_test(request):
    """
    Function-based view for donors-test endpoint.
    Fetches data from the DonorTest table and returns it as JSON.
    """

    # Query the database for all donors
    donors_test = DonorTest.objects.all().values(
        "id", "name", "email", "mobile_number", "amount_donated"
    )

    # Return the data as a JSON response
    return JsonResponse(list(donors_test), safe=False)
