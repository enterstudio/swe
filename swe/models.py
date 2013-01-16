from decimal import Decimal, ROUND_UP
import datetime
import logging
import os
from time import strftime, gmtime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from coupons.models import DiscountClaim


def nearest_cent(x):
    return Decimal(x).quantize(Decimal('1.00'), rounding=ROUND_UP)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    resetpassword_key = models.CharField(max_length=40, null=True)
    resetpassword_expires = models.DateTimeField(null=True)
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
        choicelist = [('', _('-- Select field of study --'))]
        for category in categories:
            choicegroup = []
            subjects = category.subject_set.all().order_by('display_order')
            for subject in subjects:
                if subject.is_enabled:
                    choicegroup.append((subject.pk,_(subject.display_text)))
            choicelist.append((_(category.display_text.upper()), choicegroup))
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
        choicelist = [('', _('-- Select word count --'))]
        for wordcount in wordcounts:
            choicelist.append( (wordcount.pk, wordcount.display_text()) )
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
            display_text = _(servicetype.display_text)+'  ('+pricepoint.display_text()+')'
            choicelist.append((pricepoint.pk, display_text))
        return choicelist

    def display_text(self):
        if self.min_words is None:
            if self.max_words is None:
                text = _('Any word count')
            else:
                # Translator: Used in phrase "Fewer than ## words"
                text = _('Fewer than ')+str(self.max_words)+' '+_('Words')
        else:
            if self.max_words is None:
                # Translator: Used in phrase "More than ## words"
                text = _('More than')+' '+str(self.min_words)+' '+_('Words')
            else:
                # Translator: used in phrase "## - ## words"
                text = str(self.min_words)+' - '+str(self.max_words)+' '+_('Words')
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
            return (_('$%(amount).3f per word') % {'amount': self.dollars_per_word})
        else:
            return ('$%(amount).2f' % {'amount': self.dollars})

    def __unicode__(self):
        return self.display_text()+'|'+_(self.servicetype.display_text)+'|'+self.wordcountrange.display_text()


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
    discount_claims = models.ManyToManyField(DiscountClaim, null=True, blank=True)
    paypal_ipn_id = models.IntegerField(null=True, blank=True)

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
                             # Translator: used in phrase "Editing services, # words, service type"
            word_count_text = str(self.word_count_exact)+" "+_("words")
        else:
            word_count_text = self.wordcountrange.display_text()
        return _("Editing services")+", "+word_count_text+", "+self.servicetype.display_text

    def calculate_price(self):
        if self.pricepoint.is_price_per_word:
            self.price_full = self.pricepoint.dollars_per_word * self.word_count_exact
        else:
            self.price_full = self.pricepoint.dollars
        discount = 0;
        active_claims = self.discount_claims.all()
        for claim in active_claims:
            discount += claim.discount.get_dollars_off(self.price_full)
        self.price_after_discounts = self.price_full - discount

    def get_amount_to_pay(self):
        amount = self.price_after_discounts
        if amount == None:
            raise Exception('Payment amount is not defined.')
        return nearest_cent(max(0,self.price_after_discounts))

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
