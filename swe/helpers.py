import datetime
import random
import sha
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from paypal.standard.ipn.signals import payment_was_successful
from swe import models
import coupons


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
        order = models.ManuscriptOrder.objects.get(invoice_id=invoice)
    except models.ManuscriptOrder.DoesNotExist:
        raise Exception('Invalid invoice id #%s' % invoice)
    order.is_payment_complete = True
    order.order_received_now()
    order.save()
    user = order.customer
    email_subject = _('Thank you! Your order to Science Writing Experts is complete')
    t = loader.get_template('payment_received.txt')
    t_html = loader.get_template('payment_received.html')
    c = Context(
        {'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
         'customer_service_title': _(settings.CUSTOMER_SERVICE_TITLE),
         'invoice': invoice,
         'amount_paid': order.get_amount_to_pay(),
         'service_description': order.get_service_description(),
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

def register_user(request, username, email, password, first_name, last_name):
    new_user = User.objects.create_user(
        username = username,
        email = email,
        password = password
        )
    new_user.is_active = False
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.save()
    activation_key = create_confirmation_key(new_user)
    key_expires = get_confirmation_key_expiration()
    # Create and save their profile
    new_profile = models.UserProfile(
        user=new_user,
        activation_key=activation_key,
        key_expires=key_expires,
        active_email=email,
        active_email_confirmed=False,
        )
    # Send an email with the activation link
    email_subject = _('Please confirm your account with Science Writing Experts')
    t = loader.get_template('email/activation_request.txt')
    c = RequestContext(request, {
            'activation_key': new_profile.activation_key,
            'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
            'customer_service_title': _(settings.CUSTOMER_SERVICE_TITLE),
            })
    t_html = loader.get_template('email/activation_request.html')
    email_body = t.render(c)
    email_body_html = t_html.render(c)
    mail = EmailMultiAlternatives(
        subject=email_subject,
        body=email_body,
        from_email='support@sciencewritingexperts.com',
        to=[new_user.email],
        )
    mail.attach_alternative(email_body_html, 'text/html')
    mail.send()
    new_profile.save()
    coupons.claim_featured_discounts(request, new_user)

def check_for_promotion(request):
    now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    offers = coupons.models.FeaturedDiscount.objects.filter(offer_begins__lt=now).filter(offer_ends__gt=now)
    signup_link = mark_safe(' <a href="/register/">Sign up now!</a>')
    for offer in offers:
        messages.add_message(request, messages.WARNING, offer.promotional_text+signup_link)

