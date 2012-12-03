from datetime import datetime
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
    active_email = models.CharField(max_length=100)
    active_email_confirmed = models.BooleanField()
    def __unicode__(self):
        return self.user.username


def get_file_path(instance, oldfilename):
    ext = oldfilename.split('.')[-1]
    shortname = '.'.join(oldfilename.split('.')[0:-1])
    newfilename = "%s.%s.%s" % (shortname, uuid.uuid4(), ext)
    path = strftime('%Y/%m/%d',gmtime())
    return os.path.join('manuscripts', path, newfilename)


class FileType(models.Model):
    file_type_id = models.IntegerField()
    display_text = models.CharField(max_length=40)
    file_suffix = models.CharField(max_length=10)
    def __unicode__(self):
        return self.display_text


class Document(models.Model):
    manuscript_file = models.FileField(upload_to=get_file_path)
    original_name = models.CharField(max_length=255)
    datetime_uploaded = models.DateTimeField()
    notes = models.CharField(max_length=1000, blank=True, null=True)
    file_type = models.ForeignKey(FileType, blank=True, null=True)
    def __unicode__(self):
        return self.original_name


class SubjectList(models.Model):
    is_active = models.BooleanField()
    date_activated = models.DateTimeField(null=True)
    def get_subject_choicelist(self):
        categories = self.subjectcategory_set.all().order_by('display_order')
        choicelist = []
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
    subjectset = models.ForeignKey(SubjectList)
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
    def __unicode__(self):
        return datetime.strftime(self.date_activated, "%Y-%m-%d %H:%M:%S")


class WordCountRange(models.Model):
    servicelist = models.ForeignKey(ServiceList)
    min_words = models.IntegerField(null = True) #null signifies 0
    max_words = models.IntegerField(null = True) #null signifies inf
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
    def __unicode__(self):
        return str(self.price_point_id)+'|'+self.servicetype.display_text+'|'+self.wordcountrange.display_text()


class Coupon(models.Model):
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
    # OneToMany defined in ManuscriptEdit
    current_document_version = models.ForeignKey(Document,null=True)
    service_type = models.CharField(max_length=60)
    subject = models.ForeignKey(Subject)
    word_count_range = models.ForeignKey(WordCountRange)
    word_count_exact = models.IntegerField(null=True, blank=True)
    customer = models.ForeignKey(User)
    datetime_submitted = models.DateTimeField()
    datetime_due = models.DateTimeField()
    is_editing_complete = models.BooleanField()
    was_customer_notified = models.BooleanField()
    did_customer_retrieve = models.BooleanField()
    managing_editor = models.ForeignKey(User, related_name='assignedmanuscriptorder_set', null=True, blank=True)
    # payment
    def __unicode__(self):
        return self.title


class OriginalDocument(Document):
    manuscript_order = models.OneToOneField(ManuscriptOrder)
    def __unicode__(self):
        return self.manuscript_order.title


class EditedDocument(Document):
    manuscript_order = models.ForeignKey(ManuscriptOrder)
    parent_document = models.ForeignKey(Document,related_name='+')
    submitted_by = models.ForeignKey(User)
    def __unicode__(self):
        return self.manuscript_order.title+' Original'


class ManuscriptEdit(models.Model):
    manuscript_order = models.ForeignKey(ManuscriptOrder)
    starting_document = models.ForeignKey(Document,related_name='+')
    edited_document = models.ForeignKey(Document, null=True, blank=True, related_name='+')
    #payment
    def __unicode__(self):
        return self.manuscript_order.title+' Edit id '+self.id
