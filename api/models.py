# Create your models here.
# api/models.py

from django.db import models


class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.amount}"
