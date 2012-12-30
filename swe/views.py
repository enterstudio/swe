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
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST
from paypal.standard.forms import PayPalPaymentsForm 
from paypal.standard.ipn.forms import PayPalIPNForm
from swe.context import GlobalRequestContext
from swe import forms
from swe import models
from swe import helpers
from swe.messagecatalog import MessageCatalog


def home(request):
    return render_to_response("home/home.html", GlobalRequestContext(request, {}))


def service(request):
    return render_to_response("home/service.html", GlobalRequestContext(request, {}))


def prices(request):
    return render_to_response("home/prices.html", GlobalRequestContext(request, {}))


def about(request):
    return render_to_response("home/about.html", GlobalRequestContext(request, {}))


def privacy(request):
    return render_to_response("home/privacy.html", GlobalRequestContext(request, {}))


def terms(request):
    return render_to_response("home/terms.html", GlobalRequestContext(request, {}))


def careers(request):
    return render_to_response("home/careers.html", GlobalRequestContext(request, {}))


def contact(request):
    return render_to_response("home/contact.html", GlobalRequestContext(request, {}))


def block(request):
    return render_to_response("home/block.html", GlobalRequestContext(request, {}))


@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def login(request):
    if request.user.is_authenticated():
        messages.add_message(request,messages.INFO,'You are logged in.')
        return HttpResponseRedirect('/order/')

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data[u'email']
            password = form.cleaned_data[u'password']
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
                                         'This account is not activated. Please check your email for instructions '+
                                         'to activate this account, or request a new activation key.')
                    return HttpResponseRedirect('/activationrequest/')
            else:
                # invalid login info
                messages.add_message(request,messages.ERROR,'Invalid username or password.')
                return render_to_response("account/login.html", GlobalRequestContext(request, {'form': form}))
        else:
            # form data invalid
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
            return render_to_response("account/login.html", GlobalRequestContext(request, {'form': form}))
    else:
        # get unbound form
        form = forms.LoginForm()
        return render_to_response("account/login.html", GlobalRequestContext(request, {'form': form}))


@require_POST
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/home/')


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def account(request):
    return render_to_response("account/account.html", GlobalRequestContext(request, {}))


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def order(request):
    invoice_id = request.session.get(u'invoice_id', False)
    if invoice_id:
        try:
            m = models.ManuscriptOrder.objects.get(invoice_id=invoice_id)
        except models.ManuscriptOrder.DoesNotExist:
            raise Exception('No records matched the invoice ID in the session data: invoice_id=%s' % invoice_id)
        if m.is_payment_complete:
            del request.session[u'invoice_id'] # Prevent editing an already submitted order
            return HttpResponseRedirect('/order/')
    if request.method == 'POST':
        if not invoice_id:
            # ManuscriptOrder is not yet defined. Create one.
            m = models.ManuscriptOrder(customer=request.user)
            m.save()
            m.generate_invoice_id()
            m.save()
            request.session[u'invoice_id'] = m.invoice_id

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
        else: # Invalid form
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response("order/order_form.html", GlobalRequestContext(request, {'form': form}))
    else: #GET request
        if invoice_id: # Populate form with data from earlier order that was not submitted.
            form = forms.OrderForm(initial={
                    u'title': m.title,
                    u'subject': m.subject.pk,
                    u'word_count':m.wordcountrange.pk,                    
                    })
            return render_to_response("order/order_form.html", GlobalRequestContext(request, {'form': form}))
        else:
            form = forms.OrderForm()
            return render_to_response("order/order_form.html", GlobalRequestContext(request, {'form': form}))


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def serviceoptions(request):
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
            del request.session[u'invoice_id'] # Prevent editing an already submitted order
            return HttpResponseRedirect('/order/')
        else:
            if request.method == 'POST':
                form = forms.SelectServiceForm(request.POST, invoice_id=invoice_id)
                if form.is_valid():
                    new_data=form.cleaned_data            
                    try:
                        m.pricepoint = models.PricePoint.objects.get(pk=int(new_data[u'servicetype']))
                    except models.PricePoint.DoesNotExist:
                        raise Exception('Could not find pricepoint with pk=%s' % int(new_data[u'servicetype']))
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
                    return render_to_response('order/service_options.html', GlobalRequestContext(request, {'form': form}))
            else: #GET is expected if redirected from previous page of order form
                # Initialize form with saved data if available
                initial = {}
                if m.word_count_exact is not None:
                    initial[u'word_count_exact'] = m.word_count_exact
                if m.pricepoint is not None:
                    initial[u'servicetype'] = m.pricepoint.pk

                form = forms.SelectServiceForm(invoice_id=invoice_id, initial=initial)
                return render_to_response('order/service_options.html', GlobalRequestContext(request, {'form': form}))
                

@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def uploadmanuscript(request):
    invoice_id = request.session.get(u'invoice_id', False)
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
            del request.session[u'invoice_id'] # Prevent editing an already submitted order
            return HttpResponseRedirect('/order/')            
        else:
            if request.method == 'POST':
                #TODO verify valid file exists
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
                return render_to_response('order/upload_manuscript.html', 
                                          GlobalRequestContext(request,{ 
                            'form': s3uploadform,
                            'BUCKET_NAME': settings.AWS_STORAGE_BUCKET_NAME,
                            'UPLOAD_SUCCESSFUL': d.is_upload_confirmed,
                            'FILENAME': d.original_name,
                            }))


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def awsconfirm(request):
    # User is redirected here after a successful upload
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
            del request.session[u'invoice_id'] # Prevent editing an already submitted order
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
            m.current_document_version = models.Document.objects.get(id=d.document_ptr_id)
            m.save()
            messages.add_message(request, messages.SUCCESS, 'The file %s was uploaded successfully.' % d.original_name)
            return HttpResponseRedirect('/uploadmanuscript')


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def submit(request):
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
            del request.session[u'invoice_id'] # Prevent editing an already submitted order
            return HttpResponseRedirect('/order/')
        elif not m.order_is_ready_to_submit():
            return HttpResponseRedirect('/order/')
        else:
            if request.method == 'POST':
                # POSTs should only come here if price is free. Payments go directly to PayPal.
                if float(m.get_amount_to_pay()) < 0.01:
                    helpers.acknowledge_payment_received(invoice_id)
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
                    c = GlobalRequestContext(request, {})
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

                context["pay_button_message"] = 'Clicking the "Buy Now" button will take you away from this site. Please complete your secure payment with PayPal.'
                return render_to_response("order/submit_payment.html", GlobalRequestContext(request, context))


@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def register(request):
    if request.user.is_authenticated():
        messages.add_message(request,messages.INFO,'You already have an account. To register a separate account, please logout.')
        return HttpResponseRedirect('/account/')
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
            activation_key = helpers.create_confirmation_key(new_user)
            key_expires = helpers.get_confirmation_key_expiration()
            # Create and save their profile
            new_profile = models.UserProfile(user=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires,
                                      active_email=new_data['email'],
                                      active_email_confirmed=False,
                                      )
            # Send an email with the activation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('email/activation_request.txt')
            c = GlobalRequestContext(request, {
                    'activation_key': new_profile.activation_key,
                    'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                    'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                    })
            t_html = loader.get_template('email/activation_request.html')
            email_body = t.render(c)
            email_body_html = t_html.render(c)
            mail = EmailMultiAlternatives(
                subject=email_subject, 
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
            return render_to_response('account/register.html', GlobalRequestContext(request, { 'form': form }))
    else:
        #GET
        form = forms.RegisterForm()
        return render_to_response('account/register.html', GlobalRequestContext(request, { 'form': form }))


@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
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
                messages.add_message(request,messages.ERROR,'The activation key is not valid. Please request a new activation key.')
                return HttpResponseRedirect('/activationrequest/')
            if userprofile.key_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
                # Key expired
                messages.add_message(request,messages.ERROR,'The activation key has expired. Please request a new activation key.')
                return HttpResponseRedirect('/activationrequest/')
            else:
                # Key is good
                user_account = userprofile.user
                user_account.is_active = True
                user_account.save()        
                messages.add_message(request,messages.SUCCESS,
                                     'Your have successfully activated your account. Please login to continue.')
                email_subject = 'Welcome to Science Writing Experts!'
                t = loader.get_template('email/account_activated.txt')
                c = GlobalRequestContext(request,
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
                                  GlobalRequestContext(request, {
                    'form': form,
                    'has_key': has_key,
                    }))


@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def activationrequest(request):
    if request.method=='POST':
        #TODO: Use Captcha
        form = forms.ActivationRequestForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data[u'email'])
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, 
                                     'This email address has not been registered. '+
                                     'You must register before activating the account.')
                return render_to_response('account/activation_request.html', GlobalRequestContext(request, { 'form': form }))
            activation_key = helpers.create_confirmation_key(user)
            key_expires = helpers.get_confirmation_key_expiration()
            profile = user.userprofile
            profile.activation_key = activation_key
            profile.key_expires = key_expires
            # Send an email with the confirmation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('email/activation_request.txt')
            t_html = loader.get_template('email/activation_request.html')
            c = GlobalRequestContext(request,
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
            messages.add_message(request,messages.SUCCESS,'A new activation key has been sent to %s.' % user.email)
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/activation_request.html', GlobalRequestContext(request, { 'form': form }))
    else:
        form = forms.ActivationRequestForm()
        return render_to_response('account/activation_request.html', GlobalRequestContext(request, { 'form': form }))

@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
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
                messages.add_message(request, messages.ERROR, 'This email address is not yet registered. Please sign up.')
                return render_to_response('account/request_reset_password.html', GlobalRequestContext(request, {'form': form}))
            profile = user.userprofile
            profile.resetpassword_key = helpers.create_confirmation_key(user)
            profile.resetpassword_expires = helpers.get_confirmation_key_expiration()
            profile.save()
            # Send an email with the confirmation link
            email_subject = 'Science Writing Experts password reset'
            t = loader.get_template('email/request_reset_password.txt')
            c = GlobalRequestContext(request, {
                    'resetpassword_key': profile.resetpassword_key,
                    'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                    'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                    })
            t_html = loader.get_template('email/request_reset_password.html')
            email_body = t.render(c)
            email_body_html = t_html.render(c)
            mail = EmailMultiAlternatives(
                subject=email_subject, 
                body=email_body, 
                from_email='support@sciencewritingexperts.com', 
                to=[email], 
                bcc=['support@sciencewritingexperts.com'])
            mail.attach_alternative(email_body_html, 'text/html')
            mail.send()
            messages.add_message(request, messages.ERROR, 'An email has been sent with instructions for resetting your password.')
            return HttpResponseRedirect('/home/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/request_reset_password.html', GlobalRequestContext(request, {'form': form}))
    else: # GET blank form
        form = forms.RequestResetPasswordForm()
        return render_to_response('account/request_reset_password.html', GlobalRequestContext(request, {'form': form}))



@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def completeresetpassword(request, resetpassword_key=None):
    if request.method == 'POST':
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            resetpassword_key = form.cleaned_data[u'resetpassword_key']
            try:
                userprofile = models.UserProfile.objects.get(resetpassword_key=resetpassword_key)
            except models.UserProfile.DoesNotExist:
                messages.error(request,'This email address is not currently registered.')
                return render_to_response('account/complete_reset_password.html', GlobalRequestContext(request, {'form': form}))
                #TODO This should be prevented by form validation
            # Everything ok. Change password
            userprofile.user.set_password(form.cleaned_data[u'password'])
            messages.add_message(request, messages.SUCCESS, 
                                 'Your password has been successfully updated.')
            return HttpResponseRedirect('/login/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/complete_reset_password.html', GlobalRequestContext(request, {'form': form}))
    else:
        try:
            userprofile = models.UserProfile.objects.get(resetpassword_key=resetpassword_key)
        except models.UserProfile.DoesNotExist:
            messages.add_message(request,messages.ERROR,
                                 'This request is not valid. Please contact support.')
            return HttpResponseRedirect('/home/')
        if userprofile.resetpassword_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
            # Key expired
            messages.add_message(request,messages.ERROR,
                                 'The link has expired. Please subit a new request to reset your password.')
            return HttpResponseRedirect('/resetpassword/')
        else:
            # Key is good. Render form.
            form = forms.ResetPasswordForm(initial={
                    u'resetpassword_key': resetpassword_key})
            return render_to_response('account/complete_reset_password.html', GlobalRequestContext(request, {'form': form}))


@user_passes_test(helpers.logged_in_and_active)
@user_passes_test(helpers.is_service_available, login_url='/comebacksoon/')
def changepassword(request):
    if request.method == 'POST':
        form = forms.ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            # Everything ok. Change password
            request.user.set_password(form.cleaned_data[u'new_password'])
            request.user.save()
            messages.add_message(request, messages.SUCCESS, 
                                 'Your password has been successfully changed.')
            return HttpResponseRedirect('/account/')
        else:
            messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
            return render_to_response('account/change_password.html', GlobalRequestContext(request, {'form': form}))
    else:
        form = forms.ChangePasswordForm(request.user)
        return render_to_response('account/change_password.html', GlobalRequestContext(request, {'form': form}))


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
