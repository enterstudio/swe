import base64
import datetime
import hmac
import json
import os
import random
import sha
from django import forms
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context, RequestContext
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST
from paypal.standard.forms import PayPalPaymentsForm 
from paypal.standard.ipn.forms import PayPalIPNForm
from paypal.standard.ipn.signals import payment_was_successful
import coupons
from swe import forms
from swe import models
from swe import helpers
from swe.messagecatalog import MessageCatalog


def is_service_available(u):
    return not settings.BLOCK_SERVICE


def logged_in_and_active(u):
    return u.is_active and u.is_authenticated()


def test(request):
    current_lang = request.session['django_language']
    request.session['django_language'] = 'zh-cn'
    return HttpResponse("Your language code is %s" % current_lang)

    #from django.contrib.gis.utils import GeoIP
    #g = GeoIP()
    #ip = request.META.get('REMOTE_ADDR', None)
    #if ip:
    #    country = g.country(ip)['country_name']
    #else:
    #    country = 'United States' # default city
    #import pdb; pdb.set_trace()



def home(request):
    if not request.user.is_authenticated():
        promotions = coupons.get_featured_discounts()
        for promo in promotions:
            messages.add_message(request, 
                                 messages.WARNING, 
                                 promo.promotional_text+mark_safe(' <a href="/register/">Sign up now!</a>'))
    return render_to_response("home/home.html", RequestContext(request, {}))


def service(request):
    return render_to_response("home/service.html", RequestContext(request, {}))


def prices(request):
    return render_to_response("home/prices.html", RequestContext(request, {}))


def about(request):
    return render_to_response("home/about.html", RequestContext(request, {}))


def privacy(request):
    return render_to_response("home/privacy.html", RequestContext(request, {}))


def terms(request):
    return render_to_response("home/terms.html", RequestContext(request, {}))


def careers(request):
    return render_to_response("home/careers.html", RequestContext(request, {}))


def contact(request):
    return render_to_response("home/contact.html", RequestContext(request, {}))


def block(request):
    return render_to_response("home/block.html", RequestContext(request, {}))


@user_passes_test(is_service_available, login_url='/comebacksoon/')
def login(request):
    # Redirect if already logged in
    if request.user.is_authenticated():
        messages.add_message(request,messages.INFO,_('You are logged in.'))
        return HttpResponseRedirect('/order/')
    redirect_to = request.REQUEST.get('next', '')
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data[u'email']
            password = form.cleaned_data[u'password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active: # success
                    auth.login(request,user)
                    if redirect_to:
                        return HttpResponseRedirect(redirect_to)
                    else:
                        return HttpResponseRedirect('/order/')
                else: # inactive user
                    messages.add_message(request,messages.ERROR,
                                         _('This account is not activated. Please check your email for instructions '+
                                         'to activate this account, or request a new activation key.'))
                    return HttpResponseRedirect('/activationrequest/')
            else: # invalid login info
                messages.add_message(request,messages.ERROR,_('Invalid username or password.'))
                return render_to_response("account/login.html", RequestContext(request, {
                            'form': form,
                            'redirect_to': redirect_to,
                            }))
        else: # form data invalid
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
            return render_to_response("account/login.html", RequestContext(request, {
                        'form': form,
                        'redirect_to': redirect_to,
                        }))
    else: # get unbound form
        form = forms.LoginForm()
        return render_to_response("account/login.html", RequestContext(request, {
                    'form': form,
                    'redirect_to': redirect_to,
                    }))


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return HttpResponseRedirect('/home/')
    else:
        raise Http404


@user_passes_test(logged_in_and_active, login_url='/login/')
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def account(request):
    discounts = coupons.get_available_discounts(request.user)
    orders = request.user.manuscriptorder_set.all()
    return render_to_response(
        "account/account.html", 
        RequestContext(request, {
                'discounts': discounts,
                'orders': orders,
                }))


@user_passes_test(logged_in_and_active, login_url='/register/')
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def order(request):
    order = models.ManuscriptOrder.get_open_order(request.user)
    if request.method == 'POST':
        form = forms.OrderForm(request.POST)
        if form.is_valid():
            if not order:
                # ManuscriptOrder is not yet defined. Create one.
                order = models.ManuscriptOrder(customer=request.user)
                order.save()
                order.generate_invoice_id() #Must save first because this uses the pk
                order.save()
            new_data=form.cleaned_data
            order.title=new_data[u'title']
            try:
                order.subject=models.Subject.objects.get(pk=int(new_data[u'subject']))
            except models.Subject.DoesNotExist:
                raise Exception('Could not find Subject with pk=%s' % new_data[u'subject'])
            # If changing wordcountrange, reset fields whose values may no longer be valid: 
            #   pricepoint, word_count_exact, and servicetype
            # TODO move this to a setter on the model
            try:
                new_wordcountrange = models.WordCountRange.objects.get(pk=int(new_data[u'word_count']))
            except models.WordCountRange.DoesNotExist:
                raise Exception('Could not find WordCountRange with pk=%s' % new_data[u'word_count'])
            if order.wordcountrange != new_wordcountrange:
                order.wordcountrange = new_wordcountrange
                order.servicetype = None
                order.word_count_exact = None
                order.pricepoint = None
            order.save()
            return HttpResponseRedirect('/order/2/')
        else: # Invalid form
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response("order/order_form.html", RequestContext(request, {'form': form}))
    else: #GET request
        if order: # Populate form with data from earlier order that was not submitted.
            initial = {u'title': order.title}
            try:
                subject = order.subject.pk
                initial[u'subject'] = subject
            except:
                pass # no subject selected
            try:
                word_count = order.wordcountrange.pk
                initial[u'word_count'] = word_count
            except:
                pass # no word count selected
            form = forms.OrderForm(initial=initial)
            return render_to_response("order/order_form.html", RequestContext(request, {'form': form}))
        else:
            form = forms.OrderForm()
            return render_to_response("order/order_form.html", RequestContext(request, {'form': form}))


@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def serviceoptions(request):
    order = models.ManuscriptOrder.get_open_order(request.user)
    if not order:
        return HttpResponseRedirect('/order/1/')
    if request.method == 'POST':
        form = forms.SelectServiceForm(order, request.POST)
        if form.is_valid():
            new_data=form.cleaned_data            
            try:
                order.pricepoint = models.PricePoint.objects.get(pk=int(new_data[u'servicetype']))
            except models.PricePoint.DoesNotExist:
                raise Exception('Could not find pricepoint with pk=%s' % int(new_data[u'servicetype']))
            order.servicetype = order.pricepoint.servicetype
            try:
                order.word_count_exact = new_data[u'word_count_exact']
            except KeyError:
                order.word_count_exact = None
            order.save()
            if request.POST.get(u'back'): # Go back after saving
                return HttpResponseRedirect('/order/1/')
            else:
                return HttpResponseRedirect('/order/3/')
        else: # Invalid form
            if request.POST.get(u'back'): # Go back without saving
                return HttpResponseRedirect('/order/1/')
            else:
                messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                return render_to_response('order/service_options.html', RequestContext(request, {'form': form}))
    else: #GET is expected if redirected from previous page of order form
        # Initialize form with saved data if available
        initial = {}
        if order.word_count_exact is not None:
            initial[u'word_count_exact'] = order.word_count_exact
        if order.pricepoint is not None:
            try:
                initial[u'servicetype'] = order.pricepoint.pk
            except:
                pass # pricepoint not defined
        form = forms.SelectServiceForm(order, initial=initial)
        return render_to_response('order/service_options.html', RequestContext(request, {'form': form}))
                

@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def uploadmanuscript(request):
    def render_page(order):
        try:
            doc = order.originaldocument
        except models.OriginalDocument.DoesNotExist:
            doc = models.OriginalDocument()
            doc.manuscriptorder = order
            doc.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
            doc.manuscript_file_key = doc.create_file_key()
            doc.save()
            
        s3uploadform = forms.S3UploadForm(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_STORAGE_BUCKET_NAME,
            'uploads/'+doc.manuscript_file_key+'/${filename}',
            expires_after = datetime.timedelta(days=1),
            success_action_redirect = settings.ROOT_URL+'awsconfirm/',
            min_size=0,
            max_size=20971520, # 20 MB
            )
        return render_to_response('order/upload_manuscript.html', 
                                  RequestContext(request,{ 
                    'form': s3uploadform,
                    'BUCKET_NAME': settings.AWS_STORAGE_BUCKET_NAME,
                    'UPLOAD_SUCCESSFUL': doc.is_upload_confirmed,
                    'FILENAME': doc.original_name,
                    }))

    order = models.ManuscriptOrder.get_open_order(request.user)
    if not order:
        return HttpResponseRedirect('/order/1/')
    if request.method == 'POST':
        if request.POST.get(u'back'):
            return HttpResponseRedirect('/order/2/')
        else:
            if order.originaldocument.is_upload_confirmed:
                return HttpResponseRedirect('/order/4/')
            else:
                messages.error(request, _('You must upload a file to continue.'))
                return render_page(order)
    else:
        return render_page(order)


@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def awsconfirm(request):
    # User is redirected here after a successful upload
    order = models.ManuscriptOrder.get_open_order(request.user)
    if not order:
        return HttpResponseRedirect('/order/1/')
    try:
        doc = order.originaldocument
    except models.OriginalDocument.DoesNotExist:
        raise Exception('Could not find record for uploaded document with invoice_id=%s' % order.invoice_id)
    key = request.GET.get(u'key', None)
    if key == None:
        raise Exception('Could not find AWS file key.')
    # Split key to get path and filename
    parts = key.split('/')
    key = '/'.join(parts[1:-1])
    if key != doc.manuscript_file_key:
        raise Exception('The key from AWS %s does not match our records %s for the document with invoice_id=%s' 
                        % (key, doc.manuscript_file_key, order.invoice_id))
    filename = parts[-1]
    if filename == '':
        messages.add_message(request, messages.ERROR, _('Please choose a file to be uploaded.'))
        return HttpResponseRedirect('/order/3/')
    doc.original_name = filename
    doc.is_upload_confirmed = True
    doc.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    doc.save()
    order.current_document_version = models.Document.objects.get(id=doc.document_ptr_id)
    order.save()
    messages.add_message(request, messages.SUCCESS, 'The file %s was uploaded successfully.' % doc.original_name)
    return HttpResponseRedirect('/order/3/')


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


# Signal handler                                                                                                                               
def verify_and_process_payment(sender, **kwargs):
    ipn_obj = sender
    invoice = ipn_obj.invoice
    acknowledge_payment_received(invoice)
payment_was_successful.connect(verify_and_process_payment)


@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def submit(request):
    def render_page(request, order, selectdiscountform=None, claimdiscountform=None, dropforms=None):
        context = {}
        if float(order.get_full_price()) < 0.01: # Free service. Don't show discount forms. Clear coupons so they are not wasted.
            context['show_discounts'] = False
            order.reset_discount_claims()
            order.save()
        else:
            context['show_discounts'] = True
            # Define forms for managing discounts on order
            if not dropforms:
                dropforms = [];
                for claim in order.get_discount_claims():
                    dropforms.append({
                            'label': claim.discount.display_text, 
                            'form': coupons.forms.RemoveDiscountForm(initial={u'discount': claim.pk})
                            })
            context['dropforms'] = dropforms
            if not selectdiscountform:
                available_claims = order.get_unused_discount_claims()
                if available_claims:
                    selectdiscountform = coupons.forms.SelectDiscountForm(request.user, available_claims=available_claims)
                else:
                    selectdiscountform = None
            context['selectdiscountform'] = selectdiscountform
            if not claimdiscountform:
                claimdiscountform = coupons.forms.ClaimOrSelectDiscountForm(request.user)
            context['claimdiscountform'] = claimdiscountform
        # Define invoice data
        invoice = order.calculate_price()
        order.save()
        context['invoice'] = invoice
        if float(order.get_amount_to_pay()) < 0.01: # No payment due. Free service or 100% covered with discounts
            context['paid_service'] = False
            return render_to_response("order/submit_payment.html", RequestContext(request, context))
        else:
            context['paid_service'] = True
            # paypal button
            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": invoice['amount_due'],
                "item_name": order.get_service_description(),
                "invoice": order.invoice_id,
                "notify_url": "%s%s" % (settings.ROOT_URL, reverse('paypal-ipn')),
                "return_url": "%s%s" % (settings.ROOT_URL, 'paymentreceived/'),
                "cancel_return": "%s%s" % (settings.ROOT_URL, 'paymentcanceled/'),
                }
            form = PayPalPaymentsForm(initial=paypal_dict)
            if settings.RACK_ENV=='production':
                context["pay_button"] = form.render()
            else:
                context["pay_button"] = form.sandbox()
            context["pay_button_message"] = _('Clicking the "Buy Now" button will take you away from this site. Please complete your secure payment with PayPal.')
            return render_to_response("order/submit_payment.html", RequestContext(request, context))

    order = models.ManuscriptOrder.get_open_order(request.user)
    if not order:
        return HttpResponseRedirect('/order/1/')
    if not order.order_is_ready_to_submit():
        messages.error(request, _('The order is not complete. Please review the order and supply all needed information.'))
        return HttpResponseRedirect('/order/1/')
    if request.method == 'POST':
        if request.POST.get(u'back'):
            return HttpResponseRedirect('/order/3/')
        if request.POST.get(u'remove'):
            dropform = coupons.forms.RemoveDiscountForm(request.POST)
            if dropform.is_valid():
                new_data = dropform.cleaned_data
                order.discount_claims.remove(new_data[u'discount'])
                order.save()
                return render_page(request, order)
            else:
                return render_page(request, order)
        if request.POST.get(u'select'):
            available_claims = request.user.discountclaim_set.all()
            selectdiscountform = coupons.forms.SelectDiscountForm(request.user, available_claims, request.POST)
            if selectdiscountform.is_valid():
                new_data = selectdiscountform.cleaned_data
                order.add_discount_claim(new_data[u'discount'])
                order.save()
                return render_page(request, order)
            else:
                order.discount_claims.clear()
                order.save()
                return render_page(request, order)
        if request.POST.get(u'claim'):
            claimdiscountform=coupons.forms.ClaimOrSelectDiscountForm(request.user, request.POST)
            if claimdiscountform.is_valid():
                code = claimdiscountform.cleaned_data[u'promotional_code']
                try:
                    already_claimed = coupons.models.Discount.objects.get(promotional_code=code).is_claimed_by_user(request.user)
                    if already_claimed:
                        # can't claim again, but select it instead
                        order.add_discount_claim(already_claimed)
                        order.save()
                        return render_page(request, order)
                except coupons.models.Discount.DoesNotExist:
                    Exception('Discount code was validated in form, but we could not find it.')
                claim = coupons.claim_discount(request, request.user, code)
                order.add_discount_claim(claim)
                order.save()
                return render_page(request, order)
            else:
                messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                return render_page(request, order, claimdiscountform=claimdiscountform) # With errors
        if request.POST.get(u'submit-order'):
            # POSTs should only come here if price is free. Payments go directly to PayPal.
            if float(order.get_amount_to_pay()) < 0.01:
                acknowledge_payment_received(order.invoice_id)
                messages.add_message(request, messages.INFO,
                                     _('Thank you! Your order is complete. You should receive an email confirming your order.'))
                return HttpResponseRedirect('/home/')
            else:
                raise Exception('Invoice %s was submitted as a free trial, but payment is due.' % order.invoice_id)
        else:
            raise Exception('Invoice %s was submitted by POST but the command name was not recognized.' % order.invoice_id)
    else:
        return render_page(request, order)


@user_passes_test(is_service_available, login_url='/comebacksoon/')
def register(request):
    if request.user.is_authenticated():
        messages.add_message(request,messages.INFO,_('You already have an account. To register a separate account, please logout.'))
        return HttpResponseRedirect('/account/')
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data
            new_user = User.objects.create_user(
                username = new_data[u'email'],
                email = new_data[u'email'],
                password = new_data[u'password'],
                )
            new_user.is_active = False
            new_user.first_name = new_data[u'first_name'],
            new_user.last_name = new_data['last_name'],
            new_user.save()
            new_profile = models.UserProfile(
                user=new_user,
                active_email=new_user.email,
                active_email_confirmed=False,
                )
            key = new_profile.create_activation_key()
            new_profile.save()
            coupons.claim_featured_discounts(request, new_user)
            # Send an email with the activation link
            email_subject = _('Please confirm your account with Science Writing Experts')
            t = loader.get_template('email/activation_request.txt')
            c = RequestContext(request, {
                    'activation_key': key,
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
            messages.add_message(request,messages.WARNING,
                _('An activation key has been sent to your email address. Please check your email to finish creating your account.'))
            return HttpResponseRedirect('/confirm/')
        else: # invalid form
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/register.html', RequestContext(request, { 'form': form }))
    else:
        #GET
        form = forms.RegisterForm()
        return render_to_response('account/register.html', RequestContext(request, { 'form': form }))


@user_passes_test(is_service_available, login_url='/comebacksoon/')
def confirmactivation(request, activation_key=None):
    if request.method=='POST':
        # POST
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            activation_key = form.cleaned_data[u'activation_key']
            try:
                userprofile = models.UserProfile.objects.get(activation_key=activation_key)
            except models.UserProfile.DoesNotExist:
                # Could not find activation key
                messages.add_message(request,messages.ERROR,_('The activation key is not valid. Please request a new activation key.'))
                return HttpResponseRedirect('/activationrequest/')
            if userprofile.key_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
                # Key expired
                messages.add_message(request,messages.ERROR,_('The activation key has expired. Please request a new activation key.'))
                return HttpResponseRedirect('/activationrequest/')
            else:
                # Key is good
                user_account = userprofile.user
                user_account.is_active = True
                user_account.save()        
                messages.add_message(request,messages.SUCCESS,
                                     _('Your have successfully activated your account. Please login to continue.'))
                email_subject = _('Welcome to Science Writing Experts!')
                t = loader.get_template('email/account_activated.txt')
                c = RequestContext(request,
                                         {'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                                          'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                                          })
                t_html = loader.get_template('email/account_activated.html')
                email_body = t.render(c)
                email_body_html = t_html.render(c)
                mail = EmailMultiAlternatives(subject=email_subject, 
                                              body=email_body, 
                                              from_email='support@sciencewritingexperts.com', 
                                              to=[userprofile.user.email], 
                                              )
                mail.attach_alternative(email_body_html, 'text/html')
                mail.send()
                return HttpResponseRedirect('/login/')
        else:
            #Form not valid. Unexpected since hidden data was verified when generating form.
            raise Exception('Request to activate account was invalid.')
    else:
        # GET
        if activation_key:
            has_key = True # Will generate form to confirm activation
        else:
            has_key = False # Will only display a message instructing user how to complete activation
        form = forms.ConfirmForm(initial={u'activation_key': activation_key})
        return render_to_response('account/confirm.html',
                                  RequestContext(request, {
                    'form': form,
                    'has_key': has_key,
                    }))


@user_passes_test(is_service_available, login_url='/comebacksoon/')
def activationrequest(request):
    if request.method=='POST':
        #TODO: Use Captcha
        form = forms.ActivationRequestForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data[u'email'])
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, 
                                     _('This email address has not been registered. '+
                                     'You must register before activating the account.'))
                return render_to_response('account/activation_request.html', RequestContext(request, { 'form': form }))
            profile = user.userprofile
            key = profile.create_activation_key()
            profile.save()
            # Send an email with the confirmation link
            email_subject = _('Please confirm your account with Science Writing Experts')
            t = loader.get_template('email/activation_request.txt')
            t_html = loader.get_template('email/activation_request.html')
            c = RequestContext(request,
                                     {'activation_key': key,
                                      'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                                      'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                                      })
            email_body = t.render(c)
            email_body_html = t_html.render(c)
            mail = EmailMultiAlternatives(subject=email_subject, 
                                          body=email_body, 
                                          from_email='support@sciencewritingexperts.com', 
                                          to=[user.email], 
                                          )
            mail.attach_alternative(email_body_html,'text/html')
            mail.send()
            messages.add_message(request,messages.SUCCESS, _('A new activation key has been sent to %(email)s.') % {email: user.email})
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/activation_request.html', RequestContext(request, { 'form': form }))
    else:
        form = forms.ActivationRequestForm()
        return render_to_response('account/activation_request.html', RequestContext(request, { 'form': form }))

@user_passes_test(is_service_available, login_url='/comebacksoon/')
def requestresetpassword(request):
    if request.method=='POST':
        form = forms.RequestResetPasswordForm(request.POST)
        # TODO: Use captcha
        if form.is_valid():
            email = form.cleaned_data[u'email']
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                # TODO: If account does not exist, send email with instructions to register, so that you can't check someone's registration without alerting the user
                messages.add_message(request, messages.ERROR, _('This email address is not yet registered. Please sign up.'))
                return render_to_response('account/request_reset_password.html', RequestContext(request, {'form': form}))
            profile = user.userprofile
            key = profile.create_reset_password_key()
            profile.save()
            # Send an email with the confirmation link
            email_subject = 'Science Writing Experts password reset'
            t = loader.get_template('email/request_reset_password.txt')
            c = RequestContext(request, {
                    'resetpassword_key': key,
                    'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                    'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                    })
            t_html = loader.get_template('email/request_reset_password.html')
            email_body = t.render(c)
            email_body_html = t_html.render(c)
            mail = EmailMultiAlternatives(subject=email_subject, 
                                          body=email_body, 
                                          from_email='support@sciencewritingexperts.com', 
                                          to=[email], 
                                          )
            mail.attach_alternative(email_body_html, 'text/html')
            mail.send()
            messages.add_message(request, messages.ERROR, _('An email has been sent with instructions for resetting your password.'))
            return HttpResponseRedirect('/home/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/request_reset_password.html', RequestContext(request, {'form': form}))
    else: # GET blank form
        form = forms.RequestResetPasswordForm()
        return render_to_response('account/request_reset_password.html', RequestContext(request, {'form': form}))



@user_passes_test(is_service_available, login_url='/comebacksoon/')
def completeresetpassword(request, resetpassword_key=None):
    if request.method == 'POST':
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            resetpassword_key = form.cleaned_data[u'resetpassword_key']
            try:
                userprofile = models.UserProfile.objects.get(resetpassword_key=resetpassword_key)
            except models.UserProfile.DoesNotExist:
                messages.error(request, _('This email address is not currently registered.'))
                return render_to_response('account/complete_reset_password.html', RequestContext(request, {'form': form}))
                #TODO This should be prevented by form validation
            # Everything ok. Change password
            userprofile.user.set_password(form.cleaned_data[u'password'])
            messages.add_message(request, messages.SUCCESS, 
                                 _('Your password has been successfully updated.'))
            return HttpResponseRedirect('/login/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/complete_reset_password.html', RequestContext(request, {'form': form}))
    else:
        try:
            userprofile = models.UserProfile.objects.get(resetpassword_key=resetpassword_key)
        except models.UserProfile.DoesNotExist:
            messages.add_message(request,messages.ERROR,
                                 _('This request is not valid. Please contact support.'))
            return HttpResponseRedirect('/home/')
        if userprofile.resetpassword_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
            # Key expired
            messages.add_message(request,messages.ERROR,
                                 _('The link has expired. Please subit a new request to reset your password.'))
            return HttpResponseRedirect('/resetpassword/')
        else:
            # Key is good. Render form.
            form = forms.ResetPasswordForm(initial={
                    u'resetpassword_key': resetpassword_key})
            return render_to_response('account/complete_reset_password.html', RequestContext(request, {'form': form}))


@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def changepassword(request):
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data[u'new_password'])
            request.user.save()
            messages.add_message(request, messages.SUCCESS, 
                                 _('Your password has been successfully changed.'))
            return HttpResponseRedirect('/account/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/change_password.html', RequestContext(request, {'form': form}))
    else:
        form = forms.ChangePasswordForm(request.user)
        return render_to_response('account/change_password.html', RequestContext(request, {'form': form}))


@user_passes_test(logged_in_and_active)
@user_passes_test(is_service_available, login_url='/comebacksoon/')
def claimdiscount(request):
    if request.method == 'POST':
        form = coupons.forms.ClaimDiscountForm(request.user, request.POST)
        if form.is_valid():
            coupons.claim_discount(request, request.user, form.cleaned_data[u'promotional_code'])
            messages.add_message(request, messages.SUCCESS, _('This discount is now available in your account.'))
            return HttpResponseRedirect('/account/')
        else:
            form = coupons.forms.ClaimDiscountForm(request.user, request.POST)
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/claim_discount.html', RequestContext(request, {'form': form}))
    else:
        form = coupons.forms.ClaimDiscountForm(request.user)
        return render_to_response('account/claim_discount.html', RequestContext(request, {'form': form}))
            

@csrf_exempt
def paymentcanceled(request):
    messages.add_message(request, messages.ERROR, _('Payment failed. Please contact support for further assistance.'))
    return HttpResponseRedirect('/home/')


@csrf_exempt
def paymentreceived(request):
    messages.add_message(request, messages.SUCCESS, 
                         _('Thank you! Your order is complete. You should receive an email confirming your order.'))
    return HttpResponseRedirect('/home/')


@require_POST
@csrf_exempt
def ipn(request, item_check_callable=None):

    """
    PayPal IPN endpoint (notify_url).
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
    http://tinyurl.com/d9vu9d
    
    PayPal IPN Simulator:
    https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session
    """

    flag = None
    ipn_obj = None
    form = PayPalIPNForm(request.POST)
    if form.is_valid():
        try:
            ipn_obj = form.save(commit=False)
        except Exception, e:
            flag = "Exception while processing. (%s)" % e
    else:
        flag = "Invalid form. (%s)" % form.errors

    if ipn_obj is None:
        ipn_obj = PayPalIPN()

    ipn_obj.initialize(request)

    if flag is not None:
        ipn_obj.set_flag(flag)
    else:
        # Secrets should only be used over SSL.
        if request.is_secure() and 'secret' in request.GET:
            ipn_obj.verify_secret(form, request.GET['secret'])
        else:
            try:
                ipn_obj.verify(item_check_callable)
            except Exception, e:
                flag = "Exception while processing. (%s)" % e
    ipn_obj.save()

    return HttpResponse("OKAY")


