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
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST
from paypal.standard.forms import PayPalPaymentsForm 
from paypal.standard.ipn.forms import PayPalIPNForm
from swe.context import RequestGlobalContext
from swe import forms
from swe import models
from swe.messagecatalog import MessageCatalog
from paypal.standard.ipn.signals import payment_was_successful

def home(request):
    t = loader.get_template('home.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def service(request):
    t = loader.get_template('service.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def prices(request):
    t = loader.get_template("prices.html")
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def about(request):
    t = loader.get_template('about.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def login(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')

    if request.user.is_authenticated():
        # They already have an account; don't let them register again
        messages.add_message(request,messages.INFO,'You are logged in.')
        return HttpResponseRedirect('/order/')

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    # success
                    auth.login(request,user)
                    if user.groups.filter(name='Editors').exists() or user.groups.filter(name='Managers').exists():
                        return HttpResponseRedirect('/editor/home/')
                    else:
                        return HttpResponseRedirect('/order/')
                else:
                    # inactive user
                    messages.add_message(request,messages.ERROR,
                                         'This account is not activated. Please check your email for instructions to activate this account.')
                    t = loader.get_template('login.html')
                    c = RequestGlobalContext(request, {'form': form})
                    return HttpResponse(t.render(c))
            else:
                # invalid login info
                messages.add_message(request,messages.ERROR,'Invalid username or password.')
                t = loader.get_template('login.html')
                c = RequestGlobalContext(request, { 'form': form })
                return HttpResponse(t.render(c))
        else:
            # form data invalid
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
            t = loader.get_template('login.html')
            c = RequestGlobalContext(request, { 'form': form })
            return HttpResponse(t.render(c))
    else:
        # get unbound form
        form = forms.LoginForm()
        t = loader.get_template('login.html')
        c = RequestGlobalContext(request, { 'form': form })
        return HttpResponse(t.render(c))


def logout(request):
    # The form is just a link defined in the template. This should be by post only.
    if request.method == 'POST':
        auth.logout(request)
    return HttpResponseRedirect('/home/')


def account(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    t = loader.get_template('account.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def order(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    else:
        invoice_id = request.session.get('invoice_id', False)
        if invoice_id:
            try:
                m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
            except models.ManuscriptOrder.DoesNotExist:
                raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
            if m.is_payment_complete:
                del request.session['invoice_id']
                return HttpResponseRedirect('/order/')
        if request.method == 'POST':
            if invoice_id:
                # m is already defined
                pass
            else:
                m = models.ManuscriptOrder(customer=request.user)
                m.save()
                m.generate_invoice_id()
                m.save()
                request.session['invoice_id'] = m.invoice_id

            form = forms.OrderForm(request.POST)
            if form.is_valid():
                new_data=form.cleaned_data
                m.title=new_data[u'title']
                try:
                    m.subject=models.Subject.objects.get(pk=int(new_data[u'subject']))
                except models.Subject.DoesNotExist:
                    raise Exception('Could not find Subject with pk=%s' % new_data[u'subject'])
                # If changing wordcountrange, reset fields whose values may no longer be valid: 
                #   pricepoint, word_count_exact, and servicetype
                try:
                    new_wordcountrange = models.WordCountRange.objects.get(pk=int(new_data[u'word_count']))
                except models.WordCountRange.DoesNotExist:
                    raise Exception('Could not find WordCountRange with pk=%s' % new_data[u'word_count'])
                if m.wordcountrange != new_wordcountrange:
                    m.wordcountrange = new_wordcountrange
                    m.servicetype = None
                    m.word_count_exact = None
                    m.pricepoint = None
                m.save()
                return HttpResponseRedirect('/serviceoptions/')
            else:
                # Invalid form
                messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                t = loader.get_template('order/order_form.html')
                c = RequestGlobalContext(request, {'form': form})
                return HttpResponse(t.render(c))
        else: #GET request
            if invoice_id:
                form = forms.OrderForm(initial={
                        'title': m.title,
                        'subject': m.subject.pk,
                        'word_count':m.wordcountrange.pk,                    
                        })
            else:
                form = forms.OrderForm()

            t = loader.get_template('order/order_form.html')
            c = RequestGlobalContext(request, {
                    'form': form,
                    })
            return HttpResponse(t.render(c)) 


def serviceoptions(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    else:
        invoice_id = request.session.get('invoice_id', False)
        if not invoice_id:
            messages.add_message(request, messages.ERROR, 
                                 'Could not find order information. Please make sure cookies are enabled in your browser.'
                                 )
            return HttpResponseRedirect('/order/')
        else:
            try:
                m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
            except models.ManuscriptOrder.DoesNotExist:
                raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
            if m.is_payment_complete:
                del request.session['invoice_id']
                return HttpResponseRedirect('/order/')
            else:
                if request.method == 'POST':
                    form = forms.SelectServiceForm(request.POST, invoice_id=invoice_id)
                    if form.is_valid():
                        new_data=form.cleaned_data            
                        m.pricepoint = models.PricePoint.objects.get(pk=int(new_data[u'servicetype']))
                        m.servicetype = m.pricepoint.servicetype
                        try:
                            m.word_count_exact = new_data[u'word_count_exact']
                        except KeyError:
                            m.word_count_exact = None

                        m.save()
                        return HttpResponseRedirect('/uploadmanuscript/')
                    else:
                        # Invalid form. Same response whether invoice_id is present or not
                        messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                        t = loader.get_template('order/service_options.html')
                        c = RequestGlobalContext(request, {'form': form})
                        return HttpResponse(t.render(c))
                else: #GET is expected if redirected from previous page of order form
                    # Initialize form with saved data if available
                    initial = {}
                    if m.word_count_exact is not None:
                        initial['word_count_exact'] = m.word_count_exact
                    if m.pricepoint is not None:
                        initial['servicetype'] = m.pricepoint.pk

                    form = forms.SelectServiceForm(invoice_id=invoice_id, initial=initial)
                    t = loader.get_template('order/service_options.html')
                    c = RequestGlobalContext(request, {'form': form})
                    return HttpResponse(t.render(c))
                

def uploadmanuscript(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    else:
        invoice_id = request.session.get('invoice_id', False)
        if not invoice_id:
            messages.add_message(request, messages.ERROR, 
                                 'Could not find order information. Please make sure cookies are enabled in your browser.'
                                 )
            return HttpResponseRedirect('/order/')
        else:
            try:
                m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
            except models.ManuscriptOrder.DoesNotExist:
                raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
            if m.is_payment_complete:
                del request.session['invoice_id']
                return HttpResponseRedirect('/order/')            
            else:
                if request.method == 'POST':
                    return HttpResponseRedirect('/submit/')
                else:
                    try:
                        d = m.originaldocument
                    except models.OriginalDocument.DoesNotExist:
                        d = models.OriginalDocument()
                        d.manuscriptorder = m
                        d.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
                        d.manuscript_file_key = d.create_file_key()
                        d.save()

                    s3uploadform = forms.S3UploadForm(
                        settings.AWS_ACCESS_KEY_ID,
                        settings.AWS_SECRET_ACCESS_KEY,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        'uploads/'+d.manuscript_file_key+'/${filename}',
                        expires_after = datetime.timedelta(days=1),
                        success_action_redirect = settings.ROOT_URL+'awsconfirm/',
                        min_size=0,
                        max_size=20971520, # 20 MB
                        )
                    t = loader.get_template('order/upload_manuscript.html')
                    c = RequestGlobalContext(request,{ 
                            'form': s3uploadform,
                            'BUCKET_NAME': settings.AWS_STORAGE_BUCKET_NAME,
                            'UPLOAD_SUCCESSFUL': d.is_upload_confirmed,
                            'FILENAME': d.original_name,
                            })
                    return HttpResponse(t.render(c))

def awsconfirm(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    else:
        invoice_id = request.session.get('invoice_id', False)
        if not invoice_id:
            messages.add_message(request, messages.ERROR, 
                                 'Could not find order information. Please make sure cookies are enabled in your browser.'
                                 )
            return HttpResponseRedirect('/order/')
        else:
            try:
                m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
            except models.ManuscriptOrder.DoesNotExist:
                raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
            if m.is_payment_complete:
                del request.session['invoice_id']
                return HttpResponseRedirect('/order/')
            else:
                try:
                    d = m.originaldocument
                except models.OriginalDocument.DoesNotExist:
                    raise Exception('Could not find record for uploaded document with invoice_id=%s' % invoice_id)
                key = request.GET.get(u'key', None)
                if key == None:
                    raise Exception('Could not find AWS file key.')
                # Split key to get path and filename
                parts = key.split('/')
                key = '/'.join(parts[1:-1])
                if key != d.manuscript_file_key:
                    raise Exception('The key from AWS %s does not match our records %s for the document with invoice_id=%s' 
                                    % (key, d.manuscript_file_key, invoice_id))
                filename = parts[-1]
                if filename == '':
                    messages.add_message(request, messages.ERROR, 'Please choose a file to be uploaded.')
                    return HttpResponseRedirect('/uploadmanuscript')
                d.original_name = filename
                d.is_upload_confirmed = True
                d.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
                d.save()
                messages.add_message(request, messages.SUCCESS, 'The file %s was uploaded successfully.' % d.original_name)
                return HttpResponseRedirect('/uploadmanuscript')


def submit(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    else:
        invoice_id = request.session.get('invoice_id', False)
        if not invoice_id:
            messages.add_message(request, messages.ERROR, 
                                 'Could not find order information. Please make sure cookies are enabled in your browser.'
                                 )
            return HttpResponseRedirect('/order/')
        else:
            try:
                m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
            except models.ManuscriptOrder.DoesNotExist:
                raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
            if m.is_payment_complete:
                del request.session['invoice_id']
                return HttpResponseRedirect('/order/')
            elif not m.order_is_ready_to_submit():
                return HttpResponseRedirect('/order/')
            else:
                if request.method == 'POST':
                    # POSTs should only come here if price is free. Payments go directly to PayPal.
                    if float(m.get_amount_to_pay()) < 0.01:
                        acknowledge_payment_received(invoice_id)
                        messages.add_message(request, messages.INFO,
                                             'Thank you! Your order is complete. You should receive an email confirming your order.'
                                             )
                        return HttpResponseRedirect('/home/')
                    else:
                        raise Exception('Invoice %s was submitted as a free trial, but payment is due.' % invoice_id)
                else:
                    m.calculate_price()
                    m.save()
                    invoice = {
                        'rows': [
                            {'description': m.get_service_description(), 
                             'amount': m.get_amount_to_pay()},
                            ],
                        'subtotal': m.get_amount_to_pay(),
                        'tax': '0.00',
                        'amount_due': m.get_amount_to_pay(),
                        }
                    context = {}
                    context['invoice_id'] = invoice_id
                    context['invoice'] = invoice
                    #Render payment form
                    if float(m.get_amount_to_pay()) < 0.01: # Free order, no payment due
                        t = loader.get_template('order/submit_order_free.html')
                        c = RequestGlobalContext(request, {})
                        context["pay_button"] = t.render(c)
                        context["pay_button_message"] = ''
                    else:
                        paypal_dict = {
                            "business": settings.PAYPAL_RECEIVER_EMAIL,
                            "amount": invoice['amount_due'],
                            "item_name": m.get_service_description(),
                            "invoice": invoice_id,
                            "notify_url": "%s%s" % (settings.ROOT_URL, reverse('paypal-ipn')),
                            "return_url": "%s%s" % (settings.ROOT_URL, 'paymentreceived/'),
                            "cancel_return": "%s%s" % (settings.ROOT_URL, 'paymentcanceled/'),
                            }
                        form = PayPalPaymentsForm(initial=paypal_dict)
                        if settings.RACK_ENV=='production':
                            context["pay_button"] = form.render()
                        else:
                            context["pay_button"] = form.sandbox()

                    context["pay_button_message"] = 'Payment will be completed through PayPal'
                    context = RequestGlobalContext(request, context)
                    return render_to_response("order/submit_payment.html", context)


#                m.current_document_version = models.Document.objects.get(id=d.document_ptr_id)


def create_confirmation_key(user):
    # Build the confirmation key for activation or password reset
    salt = sha.new(str(random.random())).hexdigest()[:5]
    confirmation_key = sha.new(salt+user.email).hexdigest()
    return confirmation_key


def get_confirmation_key_expiration():
    key_expires = datetime.datetime.today() + datetime.timedelta(7)
    return key_expires


def register(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if request.user.is_authenticated():
        # They already have an account; don't let them register again
        messages.add_message(request,messages.INFO,'You already have an account. To register a separate account, please logout.')
        return HttpResponseRedirect('/order/')
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data;
            new_user = User.objects.create_user(username = new_data['email'],
                                                email = new_data['email'],
                                                password = new_data['password'])
            new_user.is_active = False
            new_user.first_name = new_data['first_name']
            new_user.last_name = new_data['last_name']
            new_user.save()
            activation_key = create_confirmation_key(new_user)
            key_expires = get_confirmation_key_expiration()
            # Create and save their profile
            new_profile = models.UserProfile(user=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires,
                                      active_email=new_data['email'],
                                      active_email_confirmed=False,
                                      )
            # Send an email with the confirmation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('email/activation_request.txt')
            c = RequestGlobalContext(request, {'activation_key': new_profile.activation_key,
                         'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                         })
            t_html = loader.get_template('email/activation_request.html')
            email_body = t.render(c)
            email_body_html = t_html.render(c)
            mail = EmailMultiAlternatives(subject=email_subject, 
                         body=email_body, 
                         from_email='support@sciencewritingexperts.com', 
                         to=[new_user.email], 
                         bcc=['support@sciencewritingexperts.com'])
            mail.attach_alternative(email_body_html, 'text/html')
            mail.send()
            new_profile.save()
            messages.add_message(request,messages.SUCCESS,
                'An activation key has been sent to your email address.')
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            # User posted invalid form
            t = loader.get_template('register.html')
            c = RequestGlobalContext(request, { 'form': form })
            return HttpResponse(t.render(c))
    else:
        #GET
        form = forms.RegisterForm()
        t = loader.get_template('register.html')
        c = RequestGlobalContext(request,
            {
             'form': form,
            })
        return HttpResponse(t.render(c))


def confirm(request, activation_key=None):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if request.method=='POST':
        # POST
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            activation_key = form.cleaned_data['activation_key']
            try:
                userprofile = models.UserProfile.objects.get(activation_key=activation_key)
            except models.UserProfile.DoesNotExist:
                # Could not find activation key
                messages.add_message(request,messages.ERROR,'The activation key is not valid. Please check that you copied it correctly.')
                t = loader.get_template('confirm.html')
                c = RequestGlobalContext(request, {'form':form})
                return HttpResponse(t.render(c))
            if userprofile.key_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
                # Key expired
                messages.add_message(request,messages.ERROR,'The activation key has expired.')
                t = loader.get_template('confirm.html')
                c = RequestGlobalContext(request,{'form':form})
                return HttpResponse(t.render(c))
            else:
                # Key is good
                user_account = userprofile.user
                user_account.is_active = True
                user_account.save()        
                messages.add_message(request,messages.SUCCESS,
                                     'Your have successfully activated your account. Please login to continue.')
                email_subject = 'Welcome to Science Writing Experts!'
                t = loader.get_template('email/account_activated.txt')
                c = RequestGlobalContext(request,
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
                                              bcc=['support@sciencewritingexperts.com'])
                mail.attach_alternative(email_body_html, 'text/html')
                mail.send()

                return HttpResponseRedirect('/login/')
        else:
            #form not valid
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
            t = loader.get_template('confirm.html')
            c = RequestGlobalContext(request,{'form':form})
            return HttpResponse(t.render(c))
    else:
        # GET
        if activation_key is not None:
            form = forms.ConfirmForm(initial={'activation_key':activation_key})
        else:
            form = forms.ConfirmForm()
        t = loader.get_template('confirm.html')
        c = RequestGlobalContext(request, {'form': form })
        return HttpResponse(t.render(c))


def activationrequest(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if request.method=='POST':
        form = forms.ActivationRequestForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data[u'email'])
            activation_key = create_confirmation_key(user)
            key_expires = get_confirmation_key_expiration()
            profile = models.UserProfile.objects.get(user=user)
            profile.activation_key = activation_key
            profile.key_expires = key_expires
            # Send an email with the confirmation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('email/activationrequest.txt')
            t_html = loader.get_template('email/activationrequest.html')
            c = RequestGlobalContext(request,
                                     {'activation_key': profile.activation_key,
                                      'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                                      'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
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
            profile.save()
            messages.add_message(request,messages.SUCCESS,'A new activation key has been sent to your email address.')
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
    else:
        form = forms.ActivationRequestForm()

    t = loader.get_template('activation_request.html')
    c = RequestGlobalContext(request, { 'form': form })
    return HttpResponse(t.render(c))


def privacy(request):
    t = loader.get_template('privacy.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def terms(request):
    t = loader.get_template('terms.html')
    c = RequestGlobalContext(request, {})
    return HttpResponse(t.render(c))


def careers(request):
    t = loader.get_template('careers.html')
    c = RequestGlobalContext(request,{})
    return HttpResponse(t.render(c))


def contact(request):
    t = loader.get_template('contact.html')
    c = RequestGlobalContext(request,{})
    return HttpResponse(t.render(c))


def passwordreset(request):
    if request.method=='POST':
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data[u'email'])
            username = request.POST['email']
            user = User.objects.get(username=form.cleaned_data[u'email'])
            user.userprofile.passwordreset_key = create_confirmation_key(user)
            user.userprofile.passwordreset_expires = get_confirmation_key_expiration()
            # TODO: If account does not exist, send email with instructions to register
            # TODO: Use captcha
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
    else:
        form = forms.PasswordResetForm()

    t = loader.get_template('password_reset.html')
    c = RequestGlobalContext(request, {'form': form})
    return HttpResponse(t.render(c))


def confirmpasswordreset(request):
    # TODO
    pass



def block(request):
    t = loader.get_template('block.html')
    c = RequestGlobalContext(request,{})
    return HttpResponse(t.render(c))


@csrf_exempt
def paymentcanceled(request):
    messages.add_message(request, messages.ERROR, 'Payment failed. Please contact support for further assistance.')
    return HttpResponseRedirect('/home/')


@csrf_exempt
def paymentreceived(request):
    messages.add_message(request, messages.SUCCESS, 
                         'Thank you! Your order is complete. You should receive an email confirming your order.')
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


# Signal handler
def verify_and_process_payment(sender, **kwargs):
    ipn_obj = sender
    invoice = ipn_obj.invoice
    acknowledge_payment_received(invoice)

payment_was_successful.connect(verify_and_process_payment)


def acknowledge_payment_received(invoice):
    m = models.ManuscriptOrder.objects.get(invoice_id=invoice)
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
