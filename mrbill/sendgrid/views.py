from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import uuid
from pprint import pprint
from accounts.models import Client, Vendor
from billing.models import Bill


@csrf_exempt
def incoming_mail_parse(request):
    print(request)
    vals = request.POST
    target_email = vals['to']
    client_id, domain = target_email.split('@')
    try:
        client = Client.objects.get(pk=uuid.UUID(client_id))
    except:
        client = None

    sender_email_raw = vals['from']
    if "<" in sender_email_raw:
        chevron_left_pos = sender_email_raw.find('<')
        chevron_right_pos = sender_email_raw.find('>')
        sender_email = sender_email_raw[chevron_left_pos + 1:chevron_right_pos]
    else:
        sender_email = sender_email_raw
    # envelope = vals['envelope']

    attachments_no = vals['attachments']
    # attachment_info = vals['attachment_info']
    pprint(vals)

    # myfile = request.FILES['myfile']
    # fs = FileSystemStorage()
    # filename = fs.save(myfile.name, myfile)
    # uploaded_file_url = fs.url(filename)
    # return render(request, 'core/simple_upload.html', {
    #     'uploaded_file_url': uploaded_file_url
    # })
    bill = Bill(
        client=client,
        email_origin=sender_email,
        email_subject=vals['subject'],
        email_content_html=vals['html'],
        email_content_txt=vals['text'],
        email_sender_ip=vals['sender_ip']
    )
    attachment_amt = vars['attachments']
    # fs = FileSystemStorage()

    for key, data in vars['attachment-info'].vals():
        if data['type'] == 'application/pdf':
            pdf = request.FILES[key]
            bill.invoice = pdf
            break
            # filename = fs.save("%s.pdf" % str(uuid.uuid4().hex), pdf)
    bill.save()
    return HttpResponse('ok')
    # return Http404()
