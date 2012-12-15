import datetime
import os
import random
import sha
from django import forms
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context
from django.utils.timezone import utc
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
    t = loader.get_template('todo.html')
    c = RequestGlobalContext(request, {'text': 'Account page'})
    return HttpResponse(t.render(c))


def order(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    if request.method == 'POST':
        try:
            if models.ManuscriptOrder.objects.get(pk=request.POST[u'order']).customer != request.user:
                # Not your manuscript. Abort!
                messages.add_message(request, messages.ERROR, 'There was an error processing your order. Please contact support.')
                return HttpResponseRedirect('/home/')
        except KeyError:
            pass
        if request.POST[u'step']==u'1': #Step 1 was submitted
            form = forms.UploadManuscriptForm(request.POST, request.FILES)
            if form.is_valid():
                new_data=form.cleaned_data;
                m = models.ManuscriptOrder(
                    title=new_data[u'title'],
                    wordcountrange=models.WordCountRange.objects.get(pk=int(new_data[u'word_count'])),
                    subject=models.Subject.objects.get(pk=int(new_data[u'subject'])),
                    customer=request.user,
                    )
                m.save()
                d = models.OriginalDocument(
                    manuscriptorder = m,
                    manuscript_file=request.FILES[u'manuscript_file'],
                    original_name =request.FILES[u'manuscript_file'].name,
                    datetime_uploaded=datetime.datetime.utcnow().replace(tzinfo=utc),
                    )
                d.save()
                m.current_document_version = models.Document.objects.get(id=d.document_ptr_id)
                m.save()
                nextform = forms.SelectServiceForm(order_pk=m.pk)
                t = loader.get_template('order/form2.html')
                c = RequestGlobalContext(request, {'form': nextform})
                return HttpResponse(t.render(c))
            else: #form1 invalid
                messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                t = loader.get_template('order/form1.html')
                c = RequestGlobalContext(request, {'form': form})
                return HttpResponse(t.render(c))
        elif (request.POST[u'step']==u'2'): #Step 2 was submitted
            form = forms.SelectServiceForm(request.POST)
            if form.is_valid():
                new_data=form.cleaned_data;
                m = models.ManuscriptOrder.objects.get(pk=int(new_data[u'order']))
                m.pricepoint = models.PricePoint.objects.get(pk=int(new_data[u'servicetype']))
                m.servicetype = m.pricepoint.servicetype
                m.datetime_submitted=datetime.datetime.utcnow().replace(tzinfo=utc)
                m.datetime_due = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(m.servicetype.hours_until_due/24)
                try:
                    m.word_count_exact = new_data[u'word_count_exact']
                except KeyError:
                    m.word_count_exact = None
                m.save()
                if m.pricepoint.is_price_per_word:
                    price_full = m.pricepoint.dollars_per_word * m.word_count_exact
                else:
                    price_full = m.pricepoint.dollars
                p = models.CustomerPayment(
                    manuscriptorder=m,
                    is_payment_complete=False,
                    price_full=price_full,
                    price_charged=price_full,
                    )
                p.save()
                invoice = {
                    'rows': [
                        {'description': m.get_service_description(), 
                         'amount': p.get_amount_to_pay()},
                        ],
                    'subtotal': p.get_amount_to_pay(),
                    'tax': '0.00',
                    'amount_due': p.get_amount_to_pay(),
                    'invoice_id': p.get_invoice_id_and_save(),
                    }
                context = {}
                context['invoice'] = invoice
                #Render payment form
                if float(p.get_amount_to_pay()) < 0.01: # Free order, no payment due
                    form = forms.SubmitOrderFreeForm(order_pk=m.pk, invoice_pk=invoice['invoice_id'])
                    t = loader.get_template('order/submit_order_free.html')
                    c = RequestGlobalContext(request, { 'form': form })
                    context["pay_button"] = t.render(c)
                    context["pay_button_message"] = ''
                else:
                    paypal_dict = {
                        "business": settings.PAYPAL_RECEIVER_EMAIL,
                        "amount": invoice['amount_due'],
                        "item_name": m.get_service_description(),
                        "invoice": invoice['invoice_id'],
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
            else: #form invalid
                messages.add_message(request, messages.ERROR, MessageCatalog.form_invalid)
                t = loader.get_template('order/form2.html')
                c = RequestGlobalContext(request, {'form': form})
                return HttpResponse(t.render(c))
        elif (request.POST[u'step']==u'3'): #Step 3 was submitted
            form = forms.SubmitOrderFreeForm(request.POST)
            if form.is_valid():
                new_data = form.cleaned_data
                invoice = new_data['invoice']
                if models.CustomerPayment.objects.get(invoice_id=invoice).manuscriptorder.customer == request.user:
                    acknowledge_payment_received(invoice)
                    messages.add_message(request, messages.SUCCESS, 'Your order has been submitted.')
                    return HttpResponseRedirect('/home/')
                else:
                    raise Exception('There was an error processing the order. Please contact support.')
            else:
                raise Exception('There was an error processing the order. Please contact support.')
        else:
            raise Exception('No valid step number was specified')
    else: # GET request
        form = forms.UploadManuscriptForm()
        t = loader.get_template('order/form1.html')
        c = RequestGlobalContext(request, {
            'form': form,
        })
        return HttpResponse(t.render(c)) 


def create_activation_key(user):
    # Build the activation key for their account
    salt = sha.new(str(random.random())).hexdigest()[:5]
    activation_key = sha.new(salt+user.email).hexdigest()
    return activation_key


def get_activation_key_expiration():
    key_expires = datetime.datetime.today() + datetime.timedelta(2)
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
            activation_key = create_activation_key(new_user)
            key_expires = get_activation_key_expiration()
            # Create and save their profile
            new_profile = models.UserProfile(user=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires,
                                      active_email=new_data['email'],
                                      active_email_confirmed=False,
                                      )
            # Send an email with the confirmation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('activation_request.txt')
            c = Context({'activation_key': new_profile.activation_key,
                         'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                         'root_url': settings.ROOT_URL,
                         })
            email_body = t.render(c)
            mail = EmailMessage(subject=email_subject, 
                         body=email_body, 
                         from_email='support@sciencewritingexperts.com', 
                         to=[new_user.email], 
                         bcc=['support@sciencewritingexperts.com'])
            mail.send()
            new_profile.save()
            messages.add_message(request,messages.SUCCESS,
                'An activation key has been sent to your email address.')
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
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
            if userprofile.key_expires < datetime.datetime.utcnow().replace(tzinfo=utc):
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
            activation_key = create_activation_key(user)
            key_expires = get_activation_key_expiration()
            profile = models.UserProfile.objects.get(user=user)
            profile.activation_key = activation_key
            profile.key_expires = key_expires
            # Send an email with the confirmation link
            email_subject = 'Please confirm your account with Science Writing Experts'
            t = loader.get_template('activationrequest.txt')
            c = Context({'activation_key': profile.activation_key,
                         'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                         'root_url': settings.ROOT_URL,
                         })
            email_body = t.render(c)
            mail = EmailMessage(subject=email_subject, 
                         body=email_body, 
                         from_email='support@sciencewritingexperts.com', 
                         to=[user.email], 
                         bcc=['support@sciencewritingexperts.com'])
            mail.send()
            profile.save()
            messages.add_message(request,messages.SUCCESS,'A new activation key has been sent to your email address.')
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
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
    messages.add_message(request, messages.SUCCESS, 'Your payment was received.')
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
    payment = models.CustomerPayment.objects.get(invoice_id=invoice)
    payment.is_payment_complete = True
    payment.save()
    order = payment.manuscriptorder
    user = order.customer
    email_subject = 'Thank you! Your order to Science Writing Experts is complete'
    t = loader.get_template('payment_received.txt')
    c = Context({'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                 'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                 'invoice': invoice,
                 'amount_paid': payment.get_amount_to_pay(),
                 'service_description': order.get_service_description(),
                 })
    email_body = t.render(c)
    mail = EmailMessage(subject=email_subject, 
                        body=email_body, 
                        from_email='support@sciencewritingexperts.com', 
                        to=[user.email], 
                        bcc=['support@sciencewritingexperts.com'])
    mail.send()
