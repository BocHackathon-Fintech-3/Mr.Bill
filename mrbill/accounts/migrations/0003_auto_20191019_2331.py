# Generated by Django 2.2.6 on 2019-10-19 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20191019_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='invoice_template',
            field=models.FileField(blank=True, null=True, upload_to='invoices_templates'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='invoice_template_img',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
