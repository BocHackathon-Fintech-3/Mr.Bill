# Generated by Django 2.2.6 on 2019-10-19 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_vendor_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='invoice_template',
            field=models.FileField(default='invoices_templates/eac.pdf', upload_to='invoices_templates'),
            preserve_default=False,
        ),
    ]
