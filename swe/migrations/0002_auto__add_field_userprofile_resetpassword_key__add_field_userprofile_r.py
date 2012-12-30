# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserProfile.resetpassword_key'
        db.add_column('swe_userprofile', 'resetpassword_key',
                      self.gf('django.db.models.fields.CharField')(max_length=40, null=True),
                      keep_default=False)

        # Adding field 'UserProfile.resetpassword_expires'
        db.add_column('swe_userprofile', 'resetpassword_expires',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserProfile.resetpassword_key'
        db.delete_column('swe_userprofile', 'resetpassword_key')

        # Deleting field 'UserProfile.resetpassword_expires'
        db.delete_column('swe_userprofile', 'resetpassword_expires')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'swe.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dollars_off': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'enabled_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_by_percent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_limited_to_select_users': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'percent_off': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'swe.document': {
            'Meta': {'object_name': 'Document'},
            'datetime_uploaded': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_upload_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manuscript_file_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'swe.editeddocument': {
            'Meta': {'object_name': 'EditedDocument', '_ormbases': ['swe.Document']},
            'parent_document': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['swe.Document']", 'unique': 'True', 'primary_key': 'True'})
        },
        'swe.manuscriptedit': {
            'Meta': {'object_name': 'ManuscriptEdit'},
            'editeddocument': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['swe.EditedDocument']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'manuscriptorder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.ManuscriptOrder']"}),
            'starting_document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.Document']"})
        },
        'swe.manuscriptorder': {
            'Meta': {'object_name': 'ManuscriptOrder'},
            'coupons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['swe.Coupon']", 'symmetrical': 'False'}),
            'current_document_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.Document']", 'null': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'datetime_due': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'datetime_submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'did_customer_retrieve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'is_editing_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_payment_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'managing_editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manuscriptorder_managed_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'paypal_ipn_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price_after_discounts': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'price_full': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'pricepoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.PricePoint']", 'null': 'True'}),
            'servicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.ServiceType']", 'null': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.Subject']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'was_customer_notified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'word_count_exact': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wordcountrange': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.WordCountRange']", 'null': 'True'})
        },
        'swe.originaldocument': {
            'Meta': {'object_name': 'OriginalDocument', '_ormbases': ['swe.Document']},
            'document_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['swe.Document']", 'unique': 'True', 'primary_key': 'True'}),
            'manuscriptorder': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['swe.ManuscriptOrder']", 'unique': 'True'})
        },
        'swe.pricepoint': {
            'Meta': {'object_name': 'PricePoint'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'dollars': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'dollars_per_word': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_price_per_word': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'servicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.ServiceType']"}),
            'wordcountrange': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.WordCountRange']"})
        },
        'swe.servicelist': {
            'Meta': {'object_name': 'ServiceList'},
            'date_activated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'swe.servicetype': {
            'Meta': {'object_name': 'ServiceType'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'hours_until_due': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'servicelist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.ServiceList']"}),
            'show_in_price_table': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'swe.subject': {
            'Meta': {'object_name': 'Subject'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subjectcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.SubjectCategory']"})
        },
        'swe.subjectcategory': {
            'Meta': {'object_name': 'SubjectCategory'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subjectlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.SubjectList']"})
        },
        'swe.subjectlist': {
            'Meta': {'object_name': 'SubjectList'},
            'date_activated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'swe.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'active_email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'active_email_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_expires': ('django.db.models.fields.DateTimeField', [], {}),
            'resetpassword_expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'resetpassword_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'swe.wordcountrange': {
            'Meta': {'object_name': 'WordCountRange'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_words': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'min_words': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'servicelist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['swe.ServiceList']"})
        }
    }

    complete_apps = ['swe']