from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models.donors_model import DonorModel
from api.serializers.donors_serializer import DonorSerializer


class DonorAPIView(APIView):
    """
    API view to handle creating and updating a donor.
    """

    def post(self, request):
        """
        Handles creating a new donor.
        """
        serializer = DonorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Automatically saves the data to DonorModel
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Handles updating an existing donor.
        """
        try:
            donor = DonorModel.objects.get(pk=pk)
        except DonorModel.DoesNotExist:
            return Response(
                {"error": "Donor not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DonorSerializer(donor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DonorListAPIView(APIView):
    """
    API view to retrieve a list of all donors.
    """

    def get(self, request):
        """
        Handles retrieving a list of all donors.
        """
        donors = DonorModel.objects.all()
        serializer = DonorSerializer(donors, many=True)  # Serialize multiple objects
        return Response(serializer.data, status=status.HTTP_200_OK)
