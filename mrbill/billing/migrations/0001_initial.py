# Generated by Django 2.2.6 on 2019-10-18 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_origin', models.CharField(max_length=254)),
                ('email_subject', models.CharField(blank=True, max_length=254)),
                ('email_content_html', models.TextField(blank=True)),
                ('email_sender_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('email_content_txt', models.TextField(blank=True)),
                ('received_on', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.FileField(upload_to='bills/%Y/%m/%d/')),
                ('invoice_2', models.FileField(blank=True, null=True, upload_to='')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('expires_on', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Client')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Payment')),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Vendor')),
            ],
        ),
    ]
