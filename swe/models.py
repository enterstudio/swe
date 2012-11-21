from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    active_email = models.CharField(max_length=100)
    active_email_confirmed = models.BooleanField()
    def __unicode__(self):
        return self.user.username

import uuid, os
from time import strftime, gmtime
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

class ServiceType(models.Model):
    service_type_id = models.IntegerField()
    display_text = models.CharField(max_length=40)
    hours_until_due = models.IntegerField()
    enabled = models.BooleanField()
    def __unicode__(self):
        return self.display_text

class Subject(models.Model):
    subject_id = models.IntegerField()
    display_text=models.CharField(max_length=40)
    enabled=models.BooleanField()
    def __unicode__(self):
        return self.display_text

class WordCountRange(models.Model):
    word_count_range_id = models.IntegerField()
    max_words = models.IntegerField(null = True) #null signifies inf
    min_words = models.IntegerField(null = True) #null signifies 0
    enabled = models.BooleanField()
    def display_text(self):
        if self.min_words is None:
            if self.max_words is None:
                text = 'Any word count'
            else:
                text = 'Less than '+str(self.max_words)+' Words'
        else:
            if self.max_words is None:
                text = 'More than '+str(self.min_words)+' Words'
            else:
                text = str(self.min_words)+' - '+str(self.max_words)+' words'
        return text
    def __unicode__(self):
        return self.display_text()

class ManuscriptOrder(models.Model):
    title = models.CharField(max_length=200)
    # OneToOne defined in OriginalDocument
    # OneToMany defined in ManuscriptEdit
    current_document_version = models.ForeignKey(Document,null=True)
    service_type = models.CharField(max_length=40)
    subject = models.ForeignKey(Subject)
    word_count_range = models.ForeignKey(WordCountRange)
    word_count_exact = models.IntegerField(null=True,blank=True)
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
