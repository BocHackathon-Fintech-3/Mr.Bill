from django.contrib import admin

from .models import Bill


class BillAdmin(admin.ModelAdmin):
    list_display = ['email_origin','vendor','client','amount','expires_on','invoice_no','status']

    actions = ['parse_bill']

    def parse_bill(self, request, queryset):
        for bill in queryset:
            bill.parse_pdf()

    parse_bill.short_description = "Parse bills"


admin.site.register(Bill, BillAdmin)
