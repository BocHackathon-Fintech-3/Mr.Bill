from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
# Create your views here.
from fbmessenger import BaseMessenger, MessengerClient


class Messenger(BaseMessenger):
    def __init__(self, page_access_token, app_secret=None):
        self.page_access_token = page_access_token
        self.app_secret = app_secret
        self.client = MessengerClient(self.page_access_token, app_secret=self.app_secret)

    def message(self, message):
        self.send({'text': 'Received: {0}'.format(message['message']['text'])}, 'RESPONSE')

    def delivery(self, message):
        pass

    def read(self, message):
        pass

    def account_linking(self, message):
        pass

    def postback(self, message):
        pass

    def optin(self, message):
        pass


def webhook(request):
    if request.method == 'GET':
        if (request.GET.get('hub.verify_token') == settings.MR_BILL_FB_VERIFY_TOKEN):
            return request.GET.get('hub.challenge')
        raise ValueError('FB_VERIFY_TOKEN does not match.')
    elif request.method == 'POST':
        messenger = Messenger(settings.MRBILL_FBPAGE_ACCESS_TOKEN)
        messenger.handle(request.get_json(force=True))
    return HttpResponse("ok")
