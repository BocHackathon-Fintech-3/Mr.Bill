from django.forms import ModelForm
from .models import Vendor


class VendorForm(ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'invoice_sending_email', 'bank_account_no', 'invoice_template']


class VendorFormBBox(ModelForm):
    class Meta:
        model = Vendor
        fields = ['amount_bbox', 'due_date_bbox', 'invoice_no_bbox']
