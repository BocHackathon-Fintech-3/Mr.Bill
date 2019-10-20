from django.db import models
from accounts.models import Client, Vendor
import pdfquery
from decimal import Decimal
from threading import Thread
from django.conf import settings
from facebook.views import Messenger
from .pdfparsing import parse_amt, parse_date


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bills')
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

    @property
    def due_date_lbl(self):
        if not self.expires_on:
            return "-"
        return self.expires_on.strftime('%d, %b %Y')

    @property
    def amount_lbl(self):
        if not self.amount:
            return "-"
        else:
            return '€%s' % str(self.amount)

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
        # import pdb; pdb.set_trace()
        self.amount = parse_amt(amount_txt)
        self.expires_on = parse_date(expires_on_txt)
        self.invoice_no = invoice_no_txt
        self.parsed = True
        self.save()

    def notify_user_initial(self):
        # Method to send a notification to user that ths invoice has been ree
        if not self.client.fbid:
            return
        from fbmessenger.elements import Text, Element, Button
        from fbmessenger.templates import GenericTemplate, ButtonTemplate

        messenger = Messenger(settings.MR_BILL_FBPAGE_ACCESS_TOKEN)
        messenger.last_message = {
            "sender": {
                "id": self.client.fbid
            }
        }
        messenger.add_res(Text(
            "Hey {first_name}! I just received a bill from {vendor_name} for the amount of {amt}. The bill is due on {due_date}".format(
                first_name=self.client.first_name,
                vendor_name=self.vendor.name,
                amt=self.amount_lbl,
                due_date=self.due_date_lbl
            )))
        elem = Element(
            title='Would you like to pay now?',
            buttons=[
                Button('postback', title='Pay Now', payload='pay_now'),
                Button('postback', title='Snooze', payload='snooze')

            ]
        )
        res = GenericTemplate(elements=[elem])
        messenger.add_res(res)
        messenger.send_notifications()
        # t = Thread(target=)
        # t.start()


class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    amount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)