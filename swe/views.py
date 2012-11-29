import datetime, random, sha
from django import forms
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from swe.context import RequestGlobalContext
from swe.forms import RegisterForm, LoginForm, SubmitManuscriptForm, ConfirmForm, ActivationRequestForm
from swe.models import UserProfile, ManuscriptOrder, OriginalDocument
from swe.messagecatalog import MessageCatalog


def home(request):
    # If logged in, add MyManuscripts to Menu
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
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    # success
                    auth.login(request,user)
                    messages.add_message(request,messages.SUCCESS,'You are logged in.')
                    if user.groups.filter(name='Editors').exists() or user.groups.filter(name='Managers').exists():
                        return HttpResponseRedirect('/editor/home/')
                    else:
                        return HttpResponseRedirect('/order/')
                else:
                    # inactive user
                    messages.add_message(request,messages.ERROR,
                                         'This account is not activated. Please check your email for instructions to activate this account.')
                    t = loader.get_template('login.html')
                    c = RequestGlobalContext(request, { 'form': form })
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
        form = LoginForm()
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
    from swe.models import WordCountRange, Subject, ServiceType, Document
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/register/')
    if request.method == 'POST':
        form = SubmitManuscriptForm(request.POST, request.FILES)
        if form.is_valid():
            new_data=form.cleaned_data;
            #submit manusript
            word_count_range=WordCountRange.objects.get(word_count_range_id=new_data[u'wordcount'])
            service_type=ServiceType.objects.get(service_type_id=new_data[u'servicetype'])
            subject=Subject.objects.get(subject_id=new_data[u'subject'])
            m = ManuscriptOrder(
                title=new_data[u'title'],
                word_count_range=word_count_range,
                service_type=service_type,
                subject=subject,
                customer=request.user,
                datetime_submitted=datetime.datetime.utcnow().replace(tzinfo=utc),
                )
            days_until_due = service_type.hours_until_due/24
            m.datetime_due = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(days_until_due)
            m.save()
            d = OriginalDocument(
                manuscript_order = m,
                manuscript_file=request.FILES[u'manuscriptfile'],
                original_name =request.FILES[u'manuscriptfile'].name,
                datetime_uploaded=datetime.datetime.utcnow().replace(tzinfo=utc),
                )
            d.save()
            m.current_document_version = Document.objects.get(id=d.document_ptr_id)
            m.save()
            messages.add_message(request,messages.SUCCESS, 'Your manuscript was uploaded.')
            t = loader.get_template('todo.html')
            c = RequestGlobalContext(request, {'text': 'Go somewhere after file upload'})
            return HttpResponse(t.render(c))
        else:
            #form invalid
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
            form = SubmitManuscriptForm()
            t = loader.get_template('submitmanuscript.html')
            c = RequestGlobalContext(request, {
                'form': form
            })
            return HttpResponse(t.render(c))
    else:
        form = SubmitManuscriptForm()
        t = loader.get_template('submitmanuscript.html')
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
        return HttpResponseRedirect('/home/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data;
            new_user = User.objects.create_user(username = new_data['email'],
                                                email = new_data['email'],
                                                password = new_data['password'])
            new_user.is_active = False
            new_user.first_name = new_data['firstname']
            new_user.last_name = new_data['lastname']
            new_user.save()
            activation_key = create_activation_key(new_user)
            key_expires = get_activation_key_expiration()
            # Create and save their profile
            new_profile = UserProfile(user=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires,
                                      active_email=new_data['email'],
                                      active_email_confirmed=False,
                                      )
            # Send an email with the confirmation link
            email_subject = 'Your new Science Writing Experts account confirmation'
            t = loader.get_template('activationrequest.txt')
            c = Context({'activation_key': new_profile.activation_key,
                         'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                         'root_url': settings.ROOT_URL,
                         })
            email_body = t.render(c)
            send_mail(email_subject, email_body, 'support@sciencewritingexperts.com', [new_user.email], fail_silently=False)
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
        form = RegisterForm()
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
        form = ConfirmForm(request.POST)
        if form.is_valid():
            activation_key = form.cleaned_data['activation_key']
            try:
                user_profile = UserProfile.objects.get(activation_key=activation_key)
            except UserProfile.DoesNotExist:
                # Could not find activation key
                messages.add_message(request,messages.ERROR,'The activation key is not valid. Please check that you copied it correctly.')
                t = loader.get_template('confirm.html')
                c = RequestGlobalContext(request, {'form':form})
                return HttpResponse(t.render(c))
            if user_profile.key_expires < datetime.datetime.utcnow().replace(tzinfo=utc):
                # Key expired
                messages.add_message(request,messages.ERROR,'The activation key has expired.')
                t = loader.get_template('confirm.html')
                c = RequestGlobalContext(request,{'form':form})
                return HttpResponse(t.render(c))
            else:
                # Key is good
                user_account = user_profile.user
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
            form = ConfirmForm(initial={'activation_key':activation_key})
        else:
            form = ConfirmForm()
        t = loader.get_template('confirm.html')
        c = RequestGlobalContext(request, {'form': form })
        return HttpResponse(t.render(c))


def activationrequest(request):
    if settings.BLOCK_SERVICE:
        return HttpResponseRedirect('/comebacksoon/')
    if request.method=='POST':
        form = ActivationRequestForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data[u'email'])
            activation_key = create_activation_key(user)
            key_expires = get_activation_key_expiration()
            profile = UserProfile.objects.get(user=user)
            profile.activation_key = activation_key
            profile.key_expires = key_expires
            # Send an email with the confirmation link
            email_subject = 'Your new Science Writing Experts account confirmation'
            t = loader.get_template('activationrequest.txt')
            c = Context({'activation_key': profile.activation_key,
                         'customer_service_name': settings.CUSTOMER_SERVICE_NAME,
                         'customer_service_title': settings.CUSTOMER_SERVICE_TITLE,
                         'root_url': settings.ROOT_URL,
                         })
            email_body = t.render(c)
            send_mail(email_subject, email_body, 'support@sciencewritingexperts.com', [user.email], fail_silently=False)
            profile.save()
            messages.add_message(request,messages.SUCCESS,'A new activation key has been sent to your email address.')
            return HttpResponseRedirect('/confirm/')
        else:
            messages.add_message(request,messages.ERROR,MessageCatalog.form_invalid)
    else:
        form = ActivationRequestForm()
    t = loader.get_template('activationrequest.html')
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


def paypal(request):
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "1.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": "%s%s" % (settings.ROOT_URL, reverse('paypal-ipn')),
        "return_url": "%s%s" % (settings.ROOT_URL, 'paymentreceived/'),
        "cancel_return": "%s%s" % (settings.ROOT_URL, 'paymentcanceled/'),
        }
    form = PayPalPaymentsForm(initial=paypal_dict)
    if settings.RACK_ENV=='production':
        context = {"form": form.render()}
    else:
        context = {"form": form.sandbox()}
    return render_to_response("paypal.html", context)


@csrf_exempt
def paymentcanceled(request):
    messages.add_message(request, messages.ERROR, 'Payment failed.')
    return HttpResponseRedirect('/home/')


@csrf_exempt
def paymentreceived(request):
    messages.add_message(request, messages.SUCCESS, 'Payment received.')
    return HttpResponseRedirect('/home/')
