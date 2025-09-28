from django.http import JsonResponse


def api_overview(request):
    """
    A simple API overview endpoint.
    """
    return JsonResponse(
        {
            "message": "Welcome to the API",
            "endpoints": [
                "/api/",
                "/api/donors/",
                "/api/donors-test/",
                "/api/address/lookup"
            ],
        }
    )
