from django.db import models
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    phone = models.CharField(max_length=254, blank=True)
    email = models.EmailField(blank=True)
    fbid = models.CharField(max_length=254)
    photo = models.TextField(blank=True)
    terms_and_conditions = models.BooleanField(default=False)
    gender = models.IntegerField(default=0),  # FB api returns a number which designates hours away from GMT
    timezone = models.CharField(max_length=255, blank=True)
    pin = models.SlugField(blank=True)

    def __str__(self):
        return '%s' % self.name

    @classmethod
    def get_client(cls, fbid):
        return cls.objects.get(fbid=fbid)

    @property
    def name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def receiving_email(self):
        return "%s@incoming.mrbill.app" % str(self.id.hex)

class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    invoice_sending_email = models.EmailField(unique=True)
    bank_account_no = models.CharField(max_length=254,blank=True)


