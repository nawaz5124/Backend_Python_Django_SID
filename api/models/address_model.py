from django.db import models
from api.models.donors_model import DonorModel 

class AddressModel(models.Model):
    donor = models.ForeignKey(DonorModel, on_delete=models.CASCADE)  # Linked to Donor
    first_line = models.CharField(max_length=255, blank=True, null=True)  # Address line 1
    street = models.CharField(max_length=255, blank=True, null=True)  # Street name
    city = models.CharField(max_length=100, blank=True, null=True)  # City
    county = models.CharField(max_length=100, blank=True, null=True)  # County
    postcode = models.CharField(max_length=20, blank=True, null=True)  # Postcode
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_line}, {self.city}, {self.postcode}"