from django.db import models
from accounts.models import Client, Vendor
import pdfquery
from decimal import Decimal


from .pdfparsing import parse_amt, parse_date
class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    email_origin = models.CharField(max_length=254)
    email_subject = models.CharField(max_length=254, blank=True)
    email_content_html = models.TextField(blank=True)
    email_sender_ip = models.GenericIPAddressField(blank=True, null=True)
    email_content_txt = models.TextField(blank=True)
    received_on = models.DateTimeField(auto_now_add=True)
    invoice = models.FileField(upload_to='bills/%Y/%m/%d/')
    invoice_2 = models.FileField(blank=True, null=True)
    # details after parsing follow
    amount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    invoice_no = models.CharField(blank=True, max_length=254)
    expires_on = models.DateTimeField(blank=True, null=True)
    payment = models.ForeignKey('billing.Payment', on_delete=models.CASCADE, blank=True, null=True)

    parsed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)

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

    def parse_pdf(self):
        # method to try and parse the bill and populate the model with the necessary values, the amount!
        if not self.vendor:
            return False
        pdf = pdfquery.PDFQuery(self.invoice.path)
        # values = pdf.extract([
        #     ('with_parent', 'LTPage[pageid=1]'),
        #     ('with_formatter', 'text'),
        #
        #     ('amount', 'LTTextLineHorizontal:in_bbox("%s")' % self.vendor.amount_bbox_pts),
        #     ('due_date', 'LTTextLineHorizontal:in_bbox("%s")' % self.vendor.due_date_bbox_pts),
        #     ('invoice_no', 'LTTextLineHorizontal:in_bbox("%s")' % self.vendor.invoice_no_bbox_pts),
        # ])

        # print(values)

        pdf.load()
        amount_txt = pdf.pq('LTTextLineHorizontal:in_bbox("%s")' % self.vendor.amount_bbox_pts).text()
        # print(amount_txt)
        expires_on_txt = pdf.pq('LTTextLineHorizontal:in_bbox("%s")' % self.vendor.due_date_bbox_pts).text()
        # print(expires_on_txt)
        invoice_no_txt = pdf.pq('LTTextLineHorizontal:in_bbox("%s")' % self.vendor.invoice_no_bbox_pts).text()
        # print(invoice_no_txt)
        #import pdb; pdb.set_trace()
        self.amount = parse_amt(amount_txt)
        self.expires_on = parse_date(expires_on_txt)
        self.invoice_no = invoice_no_txt
        self.parsed = True
        self.save()

    def notify_user_initial(self):
        # Method to send a notification to user that ths invoice has been ree
        pass


class Payment(models.Model):
    pass
