from decimal import Decimal, ROUND_UP
import datetime
import logging
import os
import sha
import random
from time import strftime, gmtime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
import coupons


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

    @classmethod
    def create_user_and_profile(cls, email=None, password=None, first_name=None, last_name=None):
        new_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            )
        new_user.is_active = False
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        profile = UserProfile(
            user=new_user,
            active_email=new_user.email,
            active_email_confirmed=False,
            )
        profile.create_activation_key()
        profile.save()
        return profile

    @classmethod
    def activate(cls, activation_key):
        if not activation_key:
            return None # Guard against activating with blank key
        try:
            userprofile = cls.objects.get(activation_key=activation_key)
        except cls.DoesNotExist:
            return None
        if userprofile.key_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
            return None
        user = userprofile.user
        user.is_active = True
        user.save()
        return user

    @classmethod
    def is_resetpassword_key_ok(cls, resetpassword_key):
        if not resetpassword_key:
            return None # Guard against resetting password with blank key
        try:
            userprofile = cls.objects.get(resetpassword_key=resetpassword_key)
        except cls.DoesNotExist:
            return None
        if userprofile.resetpassword_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
            return None
        user = userprofile.user
        return user

    def create_activation_key(self):
        self.activation_key = self._create_key()
        self.key_expires = self._get_expiration()
        return self.activation_key

    def create_reset_password_key(self):
        self.resetpassword_key = self._create_key()
        self.resetpassword_expires = self._get_expiration()
        return self.resetpassword_key

    def _create_key(self):
        salt = sha.new(str(random.random())).hexdigest()[:5]
        key = sha.new(salt+self.user.email).hexdigest()
        return key

    def _get_expiration(self):
        return datetime.datetime.utcnow().replace(tzinfo=timezone.utc) + datetime.timedelta(7)

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

    def confirm_upload(self,key):
        # Split key to get path and filename
        parts = key.split('/')
        key = '/'.join(parts[1:-1])
        if key != self.manuscript_file_key:
            raise Exception('The key from AWS %s does not match our records %s for this uploaded document.'
                            % (key, self.manuscript_file_key))
        filename = parts[-1]
        if filename == '':
            return False
        self.original_name = filename
        self.is_upload_confirmed = True
        self.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        self.save()
        return True

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
    discount_claims = models.ManyToManyField(coupons.models.DiscountClaim, null=True, blank=True)
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

    def _update_derived_price_values(self):
        if self.pricepoint.is_price_per_word:
            self.price_full = self.pricepoint.dollars_per_word * self.word_count_exact
        else:
            self.price_full = self.pricepoint.dollars
        discount = 0;
        active_claims = self.discount_claims.all()
        for claim in active_claims:
            discount += claim.discount.get_dollars_off(self.price_full)
        self.price_after_discounts = self.price_full - discount

    def get_full_price(self):
        self._update_derived_price_values()
        return self.price_full

    def get_amount_to_pay(self):
        amount = self.price_after_discounts
        if amount == None:
            raise Exception('Payment amount is not defined.')
        return nearest_cent(max(0,self.price_after_discounts))

    def order_received_now(self):
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        self.datetime_submitted = now
        self.datetime_due = now + datetime.timedelta(days=self.servicetype.hours_until_due/24)
        claims = self.discount_claims.all()
        for claim in claims:
            if not claim.discount.persists_after_use:
                claim.date_used = now

    def set_current_document_version(self, doc):
        self.current_document_version = Document.objects.get(id=doc.document_ptr_id)

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

    def get_discount_claims(self):
        return self.discount_claims.all()

    def get_unused_discount_claims(self):
        exclude_list = []
        for discount in self.get_discount_claims():
            exclude_list.append(discount.pk)
        return coupons.get_available_discounts(self.customer).exclude(pk__in=exclude_list)

    def add_discount_claim(self, new_claim):
        if not new_claim.discount.multiple_use_allowed:
            old_claims = self.discount_claims.all()
            for old_claim in old_claims:
                if not old_claim.discount.multiple_use_allowed:
                    self.discount_claims.remove(old_claim)
        self.discount_claims.add(new_claim)

    def reset_discount_claims(self):
        self.discount_claims.clear()
        
    def calculate_price(self):
        self._update_derived_price_values()
        invoice_rows = [{'description': self.get_service_description(),
                         'amount': self.price_full}]
        for claim in self.get_discount_claims():
            invoice_rows.append({'description': claim.discount.display_text,
                                 'amount': '-'+str(claim.discount.get_dollars_off(self.price_full))})
        return {
            'invoice_id': self.invoice_id,
            'rows': invoice_rows,
            'subtotal': self.get_amount_to_pay(),
            'tax': '0.00',
            'amount_due': self.get_amount_to_pay(),
            }

    @staticmethod
    def get_open_order(user):
        try:
            order = user.manuscriptorder_set.get(is_payment_complete=False)
        except ManuscriptOrder.DoesNotExist:
            return None
        except ManuscriptOrder.MultipleObjectsReturned:
            raise Exception('Multiple open orders were found.')
        return order

    def is_exact_word_count_needed(self):
        try:
            max_words = self.wordcountrange.max_words
        except:
            max_words = None
        if not max_words:
            return True
        else:
            return False

    def initialize_original_document(self):
        doc = OriginalDocument()
        doc.manuscriptorder = self
        doc.datetime_uploaded = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        doc.manuscript_file_key = doc.create_file_key()
        doc.save()
        self.save()
        return doc
            
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


# Tests -------------------------------------------------------------------------

from django.test import TestCase
from django.contrib import auth
from django.contrib.auth.models import User

class UserProfileTest(TestCase):
    """ Test methods on the UserProfile class """

    email = 'acro@batic.edu'
    password = 'p4s$w0rd'
    first_name = 'John'
    last_name = 'Doe'

    def setUp(self):
        profile = UserProfile.create_user_and_profile(
            email = self.email,
            password = self.password,
            first_name = self.first_name,
            last_name = self.last_name,
            )
        self.user = profile.user
        self.now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)

    def test_create_user_and_profile(self):
        self.assertEqual(self.user.username, self.email)
        self.assertEqual(self.user.email, self.email)
        self.assertTrue(auth.models.check_password(self.password, self.user.password))
        self.assertFalse(self.user.is_active)

        self.assertEqual(self.user.userprofile.active_email, self.email)
        self.assertEqual(self.user.userprofile.active_email_confirmed, False)
        self.assertIsNotNone(self.user.userprofile.activation_key)
        
        self.assertGreater(self.user.userprofile.key_expires, self.now)

    def test_create_activation_key(self):
        self.user.userprofile.activation_key = None
        self.user.userprofile.key_expires = None

        key = self.user.userprofile.create_activation_key()
        self.assertIsNotNone(key)
        self.assertEqual(self.user.userprofile.activation_key, key)
        self.assertGreater(self.user.userprofile.key_expires, self.now)

    def test_create_reset_password_key(self):
        self.user.userprofile.resetpassword_key = None
        self.user.userprofile.resetpassword_expires = None
        key = self.user.userprofile.create_reset_password_key()

        self.assertIsNotNone(key)
        self.assertEqual(self.user.userprofile.resetpassword_key, key)
        self.assertGreater(self.user.userprofile.resetpassword_expires, self.now)

    def test_create_key(self):
        key1 = self.user.userprofile._create_key()
        key2 = self.user.userprofile._create_key()
        self.assertNotEqual(key1, key2)

    def test_get_expiration(self):
        expiration = self.user.userprofile._get_expiration()
        self.assertGreater(expiration, self.now)

    def test_activate(self):
        self.user.userprofile.key_expires = self.now
        self.user.is_active = False

        key = self.user.userprofile.create_activation_key()
        self.user.userprofile.save()

        activated_user = self.user.userprofile.activate(key)
        self.assertEqual(activated_user, self.user)
        self.assertTrue(activated_user.is_active)

    def test_activate_neg_expired_key(self):
        self.user.is_active = False

        key = self.user.userprofile.create_activation_key()
        self.user.userprofile.key_expires = self.now #key is expired
        self.user.userprofile.save()

        activated_user = self.user.userprofile.activate(key)
        self.assertIsNone(activated_user)
        self.assertFalse(self.user.is_active)

    def test_activate_neg_blank_key(self):
        blank_key = ''
        self.user.is_active = False

        self.user.userprofile.create_activation_key()
        self.user.userprofile.activation_key = blank_key
        self.user.userprofile.save()

        activated_user = self.user.userprofile.activate(blank_key)
        self.assertIsNone(activated_user)
        self.assertFalse(self.user.is_active)

    def test_is_resetpassword_key_ok(self):
        self.user.userprofile.resetpassword_expires = self.now

        key = self.user.userprofile.create_reset_password_key()
        self.user.userprofile.save()

        reset_user = self.user.userprofile.is_resetpassword_key_ok(key)
        self.assertEqual(reset_user, self.user)

    def test_is_resetpassword_key_ok_neg_expired(self):
        key = self.user.userprofile.create_reset_password_key()
        self.user.userprofile.resetpassword_expires = self.now #key is expired
        self.user.userprofile.save()

        reset_user = self.user.userprofile.is_resetpassword_key_ok(key)
        self.assertIsNone(reset_user)

    def test_is_resetpassword_key_ok_neg_blank_key(self):
        blank_key = ''
        key = self.user.userprofile.create_reset_password_key()
        self.user.userprofile.resetpassword_key = blank_key
        self.user.userprofile.save()

        reset_user = self.user.userprofile.is_resetpassword_key_ok(blank_key)
        self.assertIsNone(reset_user)

    def test_is_resetpassword_key_ok_neg_bad_key(self):
        bad_key = 'asdfjkl'
        key = self.user.userprofile.create_reset_password_key()
        self.user.userprofile.resetpassword_key = bad_key
        self.user.userprofile.save()

        reset_user = self.user.userprofile.is_resetpassword_key_ok(key)
        self.assertIsNone(reset_user)


