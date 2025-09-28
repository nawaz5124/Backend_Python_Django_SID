from django.core.management.base import BaseCommand
from api.models.donors_model import DonorModel
from api.models.donations_model import DonationModel
from api.models.payments_model import PaymentModel

class Command(BaseCommand):
    help = "Clears all records from donors, donations, and payments tables."

    def handle(self, *args, **kwargs):
        DonorModel.objects.all().delete()
        DonationModel.objects.all().delete()
        PaymentModel.objects.all().delete()
        self.stdout.write("All records from DonorModel, DonationModel, and PaymentModel have been cleared!")