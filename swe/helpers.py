import datetime
import random
import sha
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from django.utils import timezone
from paypal.standard.ipn.signals import payment_was_successful
from swe import models

def is_service_available(u):
    return not settings.BLOCK_SERVICE


def logged_in_and_active(u):
    return u.is_active and u.is_authenticated()


def create_confirmation_key(user):
    # Build the confirmation key for activation or password reset                                                                               
    salt = sha.new(str(random.random())).hexdigest()[:5]
    confirmation_key = sha.new(salt+user.email).hexdigest()
    return confirmation_key


def get_confirmation_key_expiration():
    key_expires = datetime.datetime.utcnow().replace(tzinfo=timezone.utc) + datetime.timedelta(7)
    return key_expires


# Signal handler                                                                                                                               
def verify_and_process_payment(sender, **kwargs):
    ipn_obj = sender
    invoice = ipn_obj.invoice
    acknowledge_payment_received(invoice)
payment_was_successful.connect(verify_and_process_payment)


def acknowledge_payment_received(invoice):
    try:
        m = models.ManuscriptOrder.objects.get(invoice_id=invoice)
    except models.ManuscriptOrder.DoesNotExist:
        raise Exception('Invalid invoice id #%s' % invoice)
    m.is_payment_complete = True
    m.order_received_now()
    m.save()
    user = m.customer
    email_subject = 'Thank you! Your order to Science Writing Experts is complete'
    t = loader.get_template('payment_received.txt')
    t_html = loader.get_template('payment_received.html')
    c = Context(
        {'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
         'invoice': invoice,
         'amount_paid': m.get_amount_to_pay(),
         'service_description': m.get_service_description(),
         'root_url': settings.ROOT_URL,
         })
    email_body = t.render(c)
    email_body_html = t_html.render(c)
    mail = EmailMultiAlternatives(subject=email_subject,
                        body=email_body,
                        from_email='support@sciencewritingexperts.com',
                        to=[user.email],
                        bcc=['support@sciencewritingexperts.com'])
    mail.attach_alternative(email_body_html,'text/html')
    mail.send()
