from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.donor_test_model import DonorsTest

from .utils.postcoder import fetch_address_from_postcoder

# api/views.py


def api_overview(request):
    """
    A simple API overview endpoint.
    """
    return JsonResponse(
        {
            "message": "Welcome to the API",
            "endpoints": [
                "/api/",
                "/api/donors",
                "/api/donations",
            ],
        }
    )


class DonorsAPIView(APIView):
    """
    API endpoint to fetch a list of donors (hardcoded for now).
    """

    def get(self, request, *args, **kwargs):
        # Hardcoded donor data
        donors = [
            {"id": 1, "name": "Nawaz Mohammed", "email": "nawaz.mohammed@XXXXXXXX.com"},
            {"id": 2, "name": "Fayaz Mohammed", "email": "fayaz.mohammed@XXXXXXXX.com"},
            {"id": 3, "name": "Moin Bhavikatti", "email": "moin.bhavikatti@XXXXXXXX.com"},
        ]
        return Response(donors)


def get_donors_test(request):
    """
    API endpoint to fetch all donors from the DonorsTest table.
    """
    donors_test = DonorsTest.objects.all().values(
        "id", "name", "email", "mobile_number", "amount_donated"
    )
    return JsonResponse(list(donors_test), safe=False)


