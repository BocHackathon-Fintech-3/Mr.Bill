# Generated by Django 2.2.6 on 2019-10-19 00:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_bill_invoince_no'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bill',
            old_name='invoince_no',
            new_name='invoice_no',
        ),
    ]
