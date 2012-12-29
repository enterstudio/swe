import datetime
import logging
import os
from time import strftime, gmtime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    passwordreset_key = models.CharField(max_length=40)
    passwordreset_expires = models.DateTimeField()
    active_email = models.CharField(max_length=100)
    active_email_confirmed = models.BooleanField()
    def __unicode__(self):
        return self.user.username


class Document(models.Model):
    # Has subclasses OriginalDocument and EditedDocument
    # Foreign Key defined in ManuscriptOrder
    manuscript_file_key = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    is_upload_confirmed = models.BooleanField()
    datetime_uploaded = models.DateTimeField()
    notes = models.CharField(max_length=1000, blank=True, null=True)

    def create_file_key(self):
        newfilename = '%s' % uuid.uuid4()
        path = strftime('%Y/%m/%d', gmtime())
        return os.path.join(path, newfilename)

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
        return datetime.datetime.strftime(self.date_activated, "%Y-%m-%d %H:%M:%S")


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
        return datetime.datetime.strftime(self.date_activated, "%Y-%m-%d %H:%M:%S")


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
    # Order properties:
    invoice_id = models.IntegerField(null=True)
    customer = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, null=True)
    servicetype = models.ForeignKey(ServiceType, null=True)
    wordcountrange = models.ForeignKey(WordCountRange, null=True)
    pricepoint = models.ForeignKey(PricePoint, null=True)
    word_count_exact = models.IntegerField(null=True, blank=True)

    # Document versions:
    # OneToOne defined in OriginalDocument
    # ForeignKey defined in ManuscriptEdit
    current_document_version = models.ForeignKey(Document, null=True)

    # Payment properties:
    price_full = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    price_after_discounts = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    coupons = models.ManyToManyField(Coupon)
    paypal_ipn_id = models.IntegerField(null=True)

    #Status properties
    datetime_submitted = models.DateTimeField(null=True)
    datetime_due = models.DateTimeField(null=True)
    is_payment_complete = models.BooleanField()
    is_editing_complete = models.BooleanField()
    was_customer_notified = models.BooleanField()
    did_customer_retrieve = models.BooleanField()

    managing_editor = models.ForeignKey(User, related_name='manuscriptorder_managed_set', null=True, blank=True)

    def generate_invoice_id(self):
        if self.pk == None:
            raise Exception('Save the ManuscriptOrder before generating the invoice id, since pk is needed to calculate invoice id.')
        if self.invoice_id == None:
            offset = 24269
            self.invoice_id = self.pk + offset

    def get_service_description(self):
        if self.word_count_exact is not None:
            word_count_text = str(self.word_count_exact)+" words"
        else:
            word_count_text = self.wordcountrange.display_text()
        return "Editing services, "+word_count_text+", "+self.servicetype.display_text

    def calculate_price(self):
        if self.pricepoint.is_price_per_word:
            self.price_full = self.pricepoint.dollars_per_word * self.word_count_exact
        else:
            self.price_full = self.pricepoint.dollars
        discounts = 0 #TODO
        self.price_after_discounts = self.price_full - discounts

    def get_amount_to_pay(self):
        if self.price_after_discounts == None:
            raise Exception('Payment amount is not defined.')
        if (self.price_after_discounts<0):
            raise Exception('Invalid payment amount: %s' % self.price_after_discounts)
        return "%.2f" % self.price_after_discounts

    def order_received_now(self):
        self.datetime_submitted=datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        self.datetime_due = datetime.datetime.utcnow().replace(tzinfo=timezone.utc) + datetime.timedelta(self.servicetype.hours_until_due/24)

    def order_is_ready_to_submit(self):
        #Verify that required fields are defined
        try:
            file_is_uploaded = self.originaldocument.is_upload_confirmed
        except:
            file_is_uploaded = False
        is_ready = (
            (self.invoice_id is not None) and 
            (self.customer is not None) and 
            (self.servicetype is not None) and 
            (self.wordcountrange is not None) and 
            (self.pricepoint is not None) and 
            (self.is_payment_complete == False) and
            file_is_uploaded
            )
        return is_ready
            
    def __unicode__(self):
        return self.title


class OriginalDocument(Document):
    manuscriptorder = models.OneToOneField(ManuscriptOrder)

    def __unicode__(self):
        return self.manuscriptorder.title


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
