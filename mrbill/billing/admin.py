from django.contrib import admin

from .models import Bill


class BillAdmin(admin.ModelAdmin):
    list_display = ['email_origin', 'received_on','vendor', 'client', 'amount', 'expires_on', 'invoice_no', 'status']

    actions = ['parse_bill', 'send_fb_notification']

    def parse_bill(self, request, queryset):
        for bill in queryset:
            bill.parse_pdf()

    parse_bill.short_description = "Parse bills"

    def send_fb_notification(self, request, queryset):
        for bill in queryset:
            bill.notify_user_initial()


admin.site.register(Bill, BillAdmin)
