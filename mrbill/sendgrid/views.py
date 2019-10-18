from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import uuid
from pprint import pprint
from accounts.models import Client, Vendor

@csrf_exempt
def incoming_mail_parse(request):
    print(request)
    vals = request.POST
    target_email = vals['to']
    client_id, domain = target_email.split('@')
    try:
        client = Client.objects.get(pk=uuid.UUID(client_id))
    except:
        client=None

    sender_email_raw = vals['from']
    if "<" in sender_email_raw:
        chevron_left_pos = sender_email_raw.find('<')
        chevron_right_pos = sender_email_raw.find('>')
        sender_email = sender_email_raw[chevron_left_pos+1:chevron_right_pos]
    else:
        sender_email = sender_email_raw


    #
    # try:
    #     vendor = Vendor.objects.get(invoice_sending_email=sender_email)
    # except:
    #     vendor = None


    envelope= vals['envelope']
    subject = vals['subject']
    attachments_no = vals['attachments']
    #attachment_info = vals['attachment_info']
    pprint(vals)

    # myfile = request.FILES['myfile']
    # fs = FileSystemStorage()
    # filename = fs.save(myfile.name, myfile)
    # uploaded_file_url = fs.url(filename)
    # return render(request, 'core/simple_upload.html', {
    #     'uploaded_file_url': uploaded_file_url
    # })

    return HttpResponse('ok')
    #return Http404()
