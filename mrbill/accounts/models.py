from django.db import models
import uuid
from django.contrib.auth.models import User


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

    def is_configured(self):
        return bool(self.pin)

    def get_unpaid_bills(self):
        return self.bills.filter(payment__isnull=True)

    def has_unpaid_bills(self):
        return self.get_unpaid_bills().exists()

    def __str__(self):
        return self.hid


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, blank=True, null=True, related_name='vendor', on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    invoice_sending_email = models.EmailField(unique=True)
    bank_account_no = models.CharField(max_length=254, blank=True)

    # Invoice parsing details
    amount_bbox = models.CharField(max_length=254, blank=True)
    due_date_bbox = models.CharField(max_length=254, blank=True)
    invoice_no_bbox = models.CharField(max_length=254, blank=True)

    invoice_template = models.FileField(upload_to='invoices_templates')
    invoice_template_img = models.ImageField(blank=True, null=True)

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

    def get_payments(self):
        from billing.models import Payment
        return Payment.objects.filter(bill__vendor=self)

    def extract_pdf_img(self):
        from pdf2image import convert_from_path
        from PIL import Image
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import io, uuid
        from django.core.files.base import ContentFile

        images = convert_from_path(self.invoice_template.path, dpi=96, output_folder=None, first_page=1, last_page=1,
                                   fmt='jpg')
        img = images[0]
        # img.save('out.jpg', 'JPEG')
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG')
        # image_file = InMemoryUploadedFile(thumb_io, None, 'rotate.jpg', 'image/jpeg', thumb_io.len, None)
        self.invoice_template_img.save(
            'invoices_images/%s.jpg' % str(uuid.uuid4().hex),
            content=ContentFile(thumb_io.getvalue()),
            save=False
        )
        self.save()
