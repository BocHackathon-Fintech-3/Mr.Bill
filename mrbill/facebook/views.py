from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from fbmessenger import BaseMessenger, MessengerClient
import json, requests
from fbmessenger.elements import Text, Element, Button
from fbmessenger.templates import GenericTemplate, ButtonTemplate
from accounts.models import Client
from django.urls import reverse
from .message_utils import MsgClassifier, MsgUtils
from django.contrib.sites.models import Site


class Cmds:
    CHECK_UNPAID_BIILS = 'check_bills'
    PAY_UNPAID_BIILS = 'pay_bills'


def get_absolute_url(relative_url):
    current_site = Site.objects.get_current()
    return "%s%s" % (
        current_site.domain, relative_url
    )


def get_or_create_client(fbid):
    client, created = Client.objects.get_or_create(fbid=fbid)
    if created:
        url = '%s%s' % (settings.FB_API_URL_PERSON_PROFILE, fbid)
        status = requests.get(url, headers={"Content-Type": "application/json"},
                              params={'fields': 'first_name,last_name,profile_pic',
                                      'access_token': settings.MR_BILL_FBPAGE_ACCESS_TOKEN})
        response_text = status.text
        client_info = json.loads(response_text)
        client.first_name = client_info['first_name']
        client.last_name = client_info['last_name']
        client.photo = client_info['profile_pic']
        client.save()
    return client


class Messenger(BaseMessenger):
    def __init__(self, page_access_token, app_secret=None):
        self.page_access_token = page_access_token
        self.app_secret = app_secret
        self.client = MessengerClient(self.page_access_token, app_secret=self.app_secret)
        self._responses = []

    def add_res(self, message):
        self._responses.append(message)

    def send_msgs(self, messages=None):
        if messages:
            for m in messages:
                self.send(m.to_dict())
        else:
            for m in self._responses:
                self.send(m.to_dict())

    def send_notifications(self):
        for m in self._responses:
            self.send(m.to_dict(), 'MESSAGE_TAG', tag='NON_PROMOTIONAL_SUBSCRIPTION')

    def message(self, message):
        fbid = message['sender']['id']
        client = get_or_create_client(fbid)
        classifier = MsgClassifier(msg=message)
        responses = []
        if classifier.is_greeting():
            self.add_res(Text('Hey there {first_name}!'.format(first_name=client.first_name)))

        if not client.is_configured():
            # self.add_res(Text('It seems your account has not been configured yet. But it is very easy!'))
            #
            # self.add_res(Button(
            #     button_type="web_url",
            #     title="Let's do this!",
            #     url=get_absolute_url(reverse('fb_configuration_start')),
            #     webview_height_ratio="tall",
            #     messenger_extensions=True,
            #     share_contents=False
            # ))
            base_url = reverse('fb_configuration_start', kwargs={'client_id':str(client.pk)})
            print(base_url)
            self.add_res(GenericTemplate(elements=[Element(
                title='It seems your account has not been configured yet. But it is very easy!',
                buttons=[
                    Button(
                        button_type="web_url",
                        title="Let's do this!",
                        url=get_absolute_url(base_url),
                        webview_height_ratio="tall",
                        messenger_extensions=True,
                        share_contents=False
                    )
                ])]))
            self.send_msgs()
            return

        if classifier.is_greeting():
            elem = Element(
                title='What would you like to do?',
                buttons=[
                    Button('postback', title="Check bills",
                           payload=MsgUtils.encode_postback_command(cmd=Cmds.CHECK_UNPAID_BIILS)),
                    Button('postback', title="Pay bills",
                           payload=MsgUtils.encode_postback_command(cmd=Cmds.PAY_UNPAID_BIILS))
                ]
            )
            self.add_res(GenericTemplate(elements=[elem]))
        else:
            self.add_res(Text('Received: {0}'.format(message['message']['text'])))

        self.send_msgs()

    def delivery(self, message):
        pass

    def read(self, message):
        pass

    def account_linking(self, message):
        pass

    def postback(self, message):
        fbid = message['sender']['id']
        client = get_or_create_client(fbid)
        classifier = MsgClassifier(message)
        cmd = classifier.get_cmd()
        print("Got cmd", cmd)
        if cmd == Cmds.CHECK_UNPAID_BIILS:
            if not client.has_unpaid_bills():
                self.add_res(Text('Amazing news {first_name}. You have no outstanding bills waiting. Go get a coffee!'))
            else:
                bills = client.get_unpaid_bills()
                txt = "You have the following outstanding bills:\n"
                for bill in bills:
                    txt += "{vendor_name}: €{amount}\n".format(vendor_name=bill.vendor.name, amount=str(bill.amount))
                self.add_res(Text(txt))
                # elements=[]
                # for bill in bills:
                #     elem = Element(
                #         title='Would you like to pay now?',
                #         buttons=[
                #             Button('postback', title='Pay Now', payload='pay_now'),
                #             Button('postback', title='Snooze', payload='snooze')
                #
                #         ]
                #     )
                #     res = GenericTemplate(elements=[elem])
                #     messenger.add_res(res)
        elif cmd == Cmds.PAY_UNPAID_BIILS:
            bills = client.get_unpaid_bills()

            elements = []
            for bill in bills:
                elem = Element(
                    title='{vendor_name}: {amount}'.format(vendor_name=bill.vendor.name, amount=bill.amount_lbl),
                    subtitle='Due on {due_date}'.format(due_date=bill.due_date_lbl),
                    buttons=[
                        Button('postback', title='View', payload='view_bill'),
                        Button('postback', title='Pay', payload='pay_now'),
                    ]
                )
                elements.append(elem)
            res = GenericTemplate(elements=elements)
            self.add_res(res)
        self.send_msgs()

    def optin(self, message):
        pass


@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        if (request.GET['hub.verify_token'] == settings.MR_BILL_FB_VERIFY_TOKEN):
            return HttpResponse(request.GET['hub.challenge'])
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger = Messenger(settings.MR_BILL_FBPAGE_ACCESS_TOKEN)
        res_json = json.loads(request.body.decode('utf-8'))
        t = Thread(target=messenger.handle, args=(res_json,))
        t.start()
    return HttpResponse("ok")


def client_config(request, client_id):
    client = Client.objects.get(pk=client_id)
    url = reverse('boc_auth_account', kwargs={"client_id": client_id})
    return render(request, 'webviews/start.html', {"client": client, "url": url})
