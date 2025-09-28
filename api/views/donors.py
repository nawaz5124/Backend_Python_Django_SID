from rest_framework.response import Response
from rest_framework.views import APIView


class DonorsAPIView(APIView):
    def get(self, request):
        # Replace this with actual database query logic
        donors = [
            {"id": 1, "name": "Nawaz Mohammed", "email": "nawaz.mohammed@XXXXXXXX.com"},
            {"id": 2, "name": "Moin Bhavikatti", "email": "moin.bhavikatti@XXXXXXXX.com"},
            {"id": 3, "name": "Riyaz Mohammed", "email": "riyaz.mohammed@XXXXXXXX.com"},
            {"id": 4, "name": "Ajaz Mohammed", "email": "ajaz.mohammed@XXXXXXXX.com"},
            {"id": 5, "name": "Riyaz Mohammed", "email": "riyaz.mohammed@XXXXXXXX.com"},
            {"id": 6, "name": "Ilyaz Mohammed", "email": "ilyaz.mohammed@XXXXXXXX.com"},
        ]
        return Response(donors)
