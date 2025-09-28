from django.db import models
#from api.models.donations_model import DonationModel  # Ensure correct import

class GiftAidModel(models.Model):
#    gift_aid_id = models.AutoField(primary_key=True)  # Primary key for the gift aid record
#    donation = models.ForeignKey(DonationModel, on_delete=models.CASCADE)  # Linked to Donation
    gift_aid_consent = models.BooleanField(default=False)  # Whether gift aid consent was provided
#    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the gift aid was recorded

    def __str__(self):
        return f"GiftAid for Donation {self.donation.donation_id}"