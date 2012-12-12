from datetime import datetime
import logging
import os
from time import strftime, gmtime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from paypal.standard.ipn.signals import payment_was_successful


# Helpers
def get_file_path(instance, oldfilename):
    ext = oldfilename.split('.')[-1]
    shortname = '.'.join(oldfilename.split('.')[0:-1])
    newfilename = "%s.%s.%s" % (shortname, uuid.uuid4(), ext)
    path = strftime('%Y/%m/%d',gmtime())
    return os.path.join('manuscripts', path, newfilename)


# Signal handlers
def verify_and_process_payment(sender, **kwargs):
    ipn_obj = sender
    # Undertake some action depending upon `ipn_obj`.
    fields = ['address_city', 'address_country', 'address_country_code', 'address_name', 'address_state', 'address_status', 'address_street', 
              'address_zip', 'amount', 'amount1', 'amount2', 'amount3', 'amount_per_cycle', 'auction_buyer_id', 'auction_closing_date', 
              'auction_multi_item', 'auth_amount', 'auth_exp', 'auth_id', 'auth_status', 'business', 'case_creation_date', 'case_id', 'case_type', 
              'charset', 'clean', 'clean_fields', 'contact_phone', 'created_at', 'currency_code', 'custom', 'date_error_message', 'delete', 
              'exchange_rate', 'first_name', 'flag', 'flag_code', 'flag_info', 'for_auction', 'format', 'from_view', 'full_clean', 'get_endpoint', 
              'get_next_by_created_at', 'get_next_by_updated_at', 'get_previous_by_created_at', 'get_previous_by_updated_at', 'handling_amount', 
              'id', 'initial_payment_amount', 'initialize', 'invoice', 'ipaddress', 'is_recurring', 'is_recurring_cancel', 'is_recurring_create', 
              'is_recurring_failed', 'is_recurring_payment', 'is_recurring_skipped', 'is_subscription_cancellation', 'is_subscription_end_of_term', 
              'is_subscription_modified', 'is_subscription_signup', 'is_transaction', 'item_name', 'item_number', 'last_name', 'mc_amount1', 
              'mc_amount2', 'mc_amount3', 'mc_currency', 'mc_fee', 'mc_gross', 'mc_handling', 'mc_shipping', 'memo', 'next_payment_date', 
              'notify_version', 'num_cart_items', 'objects', 'option_name1', 'option_name2', 'outstanding_balance', 'parent_txn_id', 'password', 
              'payer_business_name', 'payer_email', 'payer_id', 'payer_status', 'payment_cycle', 'payment_date', 'payment_gross', 'payment_status', 
              'payment_type', 'pending_reason', 'period1', 'period2', 'period3', 'period_type', 'pk', 'prepare_database_save', 'product_name', 
              'product_type', 'profile_status', 'protection_eligibility', 'quantity', 'query', 'reason_code', 'reattempt', 'receipt_id', 
              'receiver_email', 'receiver_id', 'recur_times', 'recurring', 'recurring_payment_id', 'remaining_settle', 'residence_country', 
              'response', 'retry_at', 'rp_invoice_id', 'save', 'save_base', 'send_signals', 'serializable_value', 'set_flag', 'settle_amount', 
              'settle_currency', 'shipping', 'shipping_method', 'subscr_date', 'subscr_effective', 'subscr_id', 'tax', 'test_ipn', 'time_created', 
              'transaction_entity', 'transaction_subject', 'txn_id', 'txn_type', 'unique_error_message', 'updated_at', 'username', 'validate_unique', 
              'verify', 'verify_secret', 'verify_sign']
    logging.warning("Processing IPN in SWE")
    for field in fields:
        logging.warning(field +': '+ipn_obj[field])
payment_was_successful.connect(verify_and_process_payment)






# Models
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    active_email = models.CharField(max_length=100)
    active_email_confirmed = models.BooleanField()
    def __unicode__(self):
        return self.user.username


class Document(models.Model):
    # Has subclasses OriginalDocument and EditedDocument
    # Foreign Key defined in ManuscriptOrder
    manuscript_file = models.FileField(upload_to=get_file_path)
    original_name = models.CharField(max_length=255)
    datetime_uploaded = models.DateTimeField()
    notes = models.CharField(max_length=1000, blank=True, null=True)
    def __unicode__(self):
        return self.original_name


class SubjectList(models.Model):
    is_active = models.BooleanField()
    date_activated = models.DateTimeField(null=True)
    def get_subject_choicelist(self):
        categories = self.subjectcategory_set.all().order_by('display_order')
        choicelist = [('', '-- Select field of study --')]
        for category in categories:
            choicegroup = []
            subjects = category.subject_set.all().order_by('display_order')
            for subject in subjects:
                if subject.is_enabled:
                    choicegroup.append((subject.pk,subject.display_text))
            choicelist.append((category.display_text.upper(), choicegroup))
        return choicelist
    def __unicode__(self):
        return datetime.strftime(self.date_activated, "%Y-%m-%d %H:%M:%S")


class SubjectCategory(models.Model):
    subjectlist = models.ForeignKey(SubjectList)
    display_text=models.CharField(max_length=40)
    display_order = models.IntegerField()
    def __unicode__(self):
        return self.display_text


class Subject(models.Model):
    subjectcategory = models.ForeignKey(SubjectCategory)
    display_text = models.CharField(max_length=40)
    display_order = models.IntegerField()
    is_enabled=models.BooleanField()
    def __unicode__(self):
        return self.display_text


class ServiceList(models.Model):
    is_active = models.BooleanField()
    date_activated = models.DateTimeField(null=True)
    def get_wordcountrange_choicelist(self):
        wordcounts = self.wordcountrange_set.all().order_by('max_words')
        choicelist = [('', '-- Select word count --')]
        for wordcount in wordcounts:
            choicelist.append((wordcount.pk, wordcount.display_text()))
        return choicelist
    def __unicode__(self):
        return datetime.strftime(self.date_activated, "%Y-%m-%d %H:%M:%S")


class WordCountRange(models.Model):
    servicelist = models.ForeignKey(ServiceList)
    min_words = models.IntegerField(null = True) #null signifies 0
    max_words = models.IntegerField(null = True) #null signifies inf
    def get_pricepoint_choicelist(self):
        pricepoints = self.pricepoint_set.all().order_by('display_order')
        choicelist = [('','-- Select service type --')]
        for pricepoint in pricepoints:
            servicetype = pricepoint.servicetype
            display_text = servicetype.display_text+'  ('+pricepoint.display_text()+')'
            choicelist.append((pricepoint.pk, display_text))
        return choicelist
    def display_text(self):
        if self.min_words is None:
            if self.max_words is None:
                text = 'Any word count'
            else:
                text = 'Fewer than '+str(self.max_words)+' Words'
        else:
            if self.max_words is None:
                text = 'More than '+str(self.min_words)+' Words'
            else:
                text = str(self.min_words)+' - '+str(self.max_words)+' words'
        return text
    def __unicode__(self):
        return self.display_text()


class ServiceType(models.Model):
    servicelist = models.ForeignKey(ServiceList)
    display_text = models.CharField(max_length=40)
    display_order = models.IntegerField()
    hours_until_due = models.IntegerField()
    show_in_price_table = models.BooleanField()
    def __unicode__(self):
        return self.display_text


class PricePoint(models.Model):
    wordcountrange = models.ForeignKey(WordCountRange)
    servicetype = models.ForeignKey(ServiceType)
    dollars = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    dollars_per_word = models.DecimalField(null=True, max_digits=7, decimal_places=3)
    is_price_per_word = models.BooleanField()
    display_order = models.IntegerField()
    def display_text(self):
        if self.is_price_per_word:
            return ('$%.3f per word' % self.dollars_per_word)
        else:
            return ('$%.2f' % self.dollars)
    def __unicode__(self):
        return str(self.display_text())+'|'+self.servicetype.display_text+'|'+self.wordcountrange.display_text()


class Coupon(models.Model):
    # ManyToMany defined in Payment
    display_text = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    dollars_off = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    is_by_percent = models.BooleanField()
    percent_off = models.IntegerField(null=True)
    expiration_date = models.DateTimeField()
    is_limited_to_select_users = models.BooleanField()
    enabled_users = models.ManyToManyField(User)


class ManuscriptOrder(models.Model):
    title = models.CharField(max_length=200)
    # OneToOne defined in OriginalDocument
    # ForeignKey defined in ManuscriptEdit
    # ForeignKey defined in Payment
    current_document_version = models.ForeignKey(Document, null=True)
    servicetype = models.ForeignKey(ServiceType, null=True)
    wordcountrange = models.ForeignKey(WordCountRange, null=True)
    pricepoint = models.ForeignKey(PricePoint, null=True)
    word_count_exact = models.IntegerField(null=True, blank=True)
    subject = models.ForeignKey(Subject, null=True)
    customer = models.ForeignKey(User)
    datetime_submitted = models.DateTimeField(null=True)
    datetime_due = models.DateTimeField(null=True)
    is_editing_complete = models.BooleanField()
    was_customer_notified = models.BooleanField()
    did_customer_retrieve = models.BooleanField()
    managing_editor = models.ForeignKey(User, related_name='manuscriptorder_managed_set', null=True, blank=True)
    def __unicode__(self):
        return self.title


class CustomerPayment(models.Model):
    coupons = models.ManyToManyField(Coupon)
    is_payment_complete = models.BooleanField()
    manuscriptorder = models.ForeignKey(ManuscriptOrder)
    paypal_ipn_id = models.IntegerField(null=True)
    invoice_id = models.IntegerField(null=True)
    price_full = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    price_charged = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    price_paid = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    def get_amount_to_pay(self):
        amount_to_pay = self.price_full
        if (amount_to_pay<0):
            raise Exception('Invalid payment amount.')
        if amount_to_pay == None:
            raise Exception('Payment amount is not defined.')
        return "%.2f" % amount_to_pay
    def get_invoice_id_and_save(self):
        if self.invoice_id == None:
            offset = 24269
            self.invoice_id = self.pk + offset
            self.save()
        return self.invoice_id


class OriginalDocument(Document):
    manuscriptorder = models.OneToOneField(ManuscriptOrder)
    def __unicode__(self):
        return self.manuscript_order.title


class EditedDocument(Document):
    parent_document = models.OneToOneField(Document)
    def __unicode__(self):
        return self.manuscript_order.title+' Original'


class ManuscriptEdit(models.Model):
    manuscriptorder = models.ForeignKey(ManuscriptOrder)
    starting_document = models.ForeignKey(Document)
    editeddocument = models.OneToOneField(EditedDocument, null=True, blank=True)
    editor = models.OneToOneField(User)
    is_open = models.BooleanField()
    # TODO: Payment to editor
    def __unicode__(self):
        return self.manuscript_order.title+' Edit id '+self.id
