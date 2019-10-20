# Mr.Bill is in da house!
Welcome to a new way of Paying your Bills!

## Some installation instructions
This runs on Python 3.7. You will need a python virtual environment. Along with the dependencies installed, you will also need to install poppler for the pdf2image conversion to work.
There are ports for Windows & Mac as well.


 You will also need to set the following environment variables, along with the necessary keys:
 - MR_BILL_FBPAGE_ACCESS_TOKEN
 - MR_BILL_FB_VERIFY_TOKEN
 - BOC_CLIENT_ID , The BoC Sandbox client id
 - BOC_CLIENT_SECRET, The BoC Sandbox client secret
 
You also need to setup Sendgrid Inbound Parse to the host:
`<your url>/sendgrid/incoming/` . Mind the slash at the end.

For Sendgrid to work, you obviously need to point a subdomain/domain MX record to Sendgrid by following their relevant instructions.


## Running MrBill

MrBill is a good-old Django App:
- python manage.py migrate
- python manage.py runserver

Bear in mind that for connecting to your Facebook bot, you will need a tool like Ngrok or Serveo, to open an SSH Tunnel to your machine.
After doing so, you should configure your FB App webhook to point to `<your Ngrok url currently live>/facebook/webhook/`. Unfortunately,
you need to update your FB App config every time your Ngrok session expires.

## For questions?
Just hit me up!