from django.db import models
from accounts.models import Client, Vendor
import pdfquery
from decimal import Decimal
from threading import Thread
from django.conf import settings
from facebook.message_utils import MsgClassifier, MsgUtils
from facebook.views import Messenger
from .pdfparsing import parse_amt, parse_date


class Bill(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bills')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True,related_name='bills')
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
        if self.payments.exists():
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
        from facebook.views import Cmds
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

        #from boc.api_calls import get_accounts_balances
        #balances = get_accounts_balances(self.client)
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
                Button('postback', title='Pay Now', payload=MsgUtils.encode_postback_command(cmd=Cmds.PAY_BILL,
                                                                                             params={'id': str(
                                                                                                 self.id)})),
                Button('postback', title='Snooze', payload=MsgUtils.encode_postback_command(cmd=Cmds.SNOOZE_BILL,
                                                                                            params={'id': str(
                                                                                                self.id)}))

            ]
        )
        res = GenericTemplate(elements=[elem])
        messenger.add_res(res)
        messenger.send_notifications()
        # t = Thread(target=)
        # t.start()

    @property
    def is_settled(self):
        return self.payments.exists()

    def settle(self):
        try:
            payment = Payment(bill=self, amount=self.amount)
            payment.save()
            return True
        except:
            return False



class Payment(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    amount = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
