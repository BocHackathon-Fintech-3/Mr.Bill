from django.db import models
from accounts.models import Client, Vendor


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    email_origin = models.CharField(max_length=254)
    received_on = models.DateTimeField(auto_now_add=True)
    invoice = models.FileField()
    # details after parsing follow
    amount = models.DecimalField(blank=True, max_digits=10, decimal_places=2)
    expires_on = models.DateTimeField(blank=True, null=True)
    payment = models.ForeignKey('billing.Payment', on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                vendor = Vendor.objects.get(invoice_sending_email=self.email_origin)
                self.vendor = vendor
            except:
                pass
        super().save(*args, **kwargs)

    @property
    def status(self):
        if self.payment is not None:
            return 'paid'
        else:
            return 'pending'


class Payment(models.Model):
    pass
