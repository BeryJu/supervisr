from django.core.mail import send_mail

class Mail(object):

    def __init__(self, arg):
        super(Mail, self).__init__()
        self.arg = arg
