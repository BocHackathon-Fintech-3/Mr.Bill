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
    def hid(self):
        return self.id.hex

    @property
    def receiving_email(self):
        return "%s@incoming.mrbill.app" % str(self.id.hex)

    def __str__(self):
        return self.hid


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=254)
    invoice_sending_email = models.EmailField(unique=True)
    bank_account_no = models.CharField(max_length=254, blank=True)

    # Invoice parsing details
    amount_bbox = models.CharField(max_length=254, blank=True)
    due_date_bbox = models.CharField(max_length=254, blank=True)
    invoice_no_bbox = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.invoice_sending_email)

    def _get_pts_from_inch(self, coordinates):
        elements = coordinates.split(',')
        pts_elements = ["%.2f" % (float(x) * 72) for x in elements]
        return ','.join(pts_elements)

    @property
    def amount_bbox_pts(self):
        return self._get_pts_from_inch(self.amount_bbox)

    @property
    def invoice_no_bbox_pts(self):
        return self._get_pts_from_inch(self.invoice_no_bbox)

    @property
    def due_date_bbox_pts(self):
        return self._get_pts_from_inch(self.due_date_bbox)