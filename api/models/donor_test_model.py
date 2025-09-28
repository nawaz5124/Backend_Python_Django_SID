import logging

from django.db import models

logger = logging.getLogger(__name__)


class DonorTest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile_number = models.CharField(max_length=15)
    amount_donated = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False  # This tells Django not to handle migrations for this table
        db_table = "api_donortest"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:  # Check if it's an update
            logger.debug(f"Updating DonorTest: {self.name} (ID: {self.pk})")
        else:  # New record
            logger.debug(f"Creating DonorTest: {self.name}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.debug(f"Deleting DonorTest: {self.name} (ID: {self.pk})")
        super().delete(*args, **kwargs)
