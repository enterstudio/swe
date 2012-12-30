# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('swe_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('activation_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('key_expires', self.gf('django.db.models.fields.DateTimeField')()),
            ('active_email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('active_email_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('swe', ['UserProfile'])

        # Adding model 'Document'
        db.create_table('swe_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manuscript_file_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('original_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_upload_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('datetime_uploaded', self.gf('django.db.models.fields.DateTimeField')()),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('swe', ['Document'])

        # Adding model 'SubjectList'
        db.create_table('swe_subjectlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_activated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('swe', ['SubjectList'])

        # Adding model 'SubjectCategory'
        db.create_table('swe_subjectcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subjectlist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.SubjectList'])),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('swe', ['SubjectCategory'])

        # Adding model 'Subject'
        db.create_table('swe_subject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subjectcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.SubjectCategory'])),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('swe', ['Subject'])

        # Adding model 'ServiceList'
        db.create_table('swe_servicelist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_activated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('swe', ['ServiceList'])

        # Adding model 'WordCountRange'
        db.create_table('swe_wordcountrange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('servicelist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.ServiceList'])),
            ('min_words', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('max_words', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('swe', ['WordCountRange'])

        # Adding model 'ServiceType'
        db.create_table('swe_servicetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('servicelist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.ServiceList'])),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
            ('hours_until_due', self.gf('django.db.models.fields.IntegerField')()),
            ('show_in_price_table', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('swe', ['ServiceType'])

        # Adding model 'PricePoint'
        db.create_table('swe_pricepoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wordcountrange', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.WordCountRange'])),
            ('servicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.ServiceType'])),
            ('dollars', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('dollars_per_word', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=3)),
            ('is_price_per_word', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('swe', ['PricePoint'])

        # Adding model 'Coupon'
        db.create_table('swe_coupon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('dollars_off', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('is_by_percent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('percent_off', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_limited_to_select_users', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('swe', ['Coupon'])

        # Adding M2M table for field enabled_users on 'Coupon'
        db.create_table('swe_coupon_enabled_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('coupon', models.ForeignKey(orm['swe.coupon'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('swe_coupon_enabled_users', ['coupon_id', 'user_id'])

        # Adding model 'ManuscriptOrder'
        db.create_table('swe_manuscriptorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.Subject'], null=True)),
            ('servicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.ServiceType'], null=True)),
            ('wordcountrange', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.WordCountRange'], null=True)),
            ('pricepoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.PricePoint'], null=True)),
            ('word_count_exact', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_document_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.Document'], null=True)),
            ('price_full', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('price_after_discounts', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('paypal_ipn_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('datetime_submitted', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('datetime_due', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('is_payment_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_editing_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('was_customer_notified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('did_customer_retrieve', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('managing_editor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='manuscriptorder_managed_set', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('swe', ['ManuscriptOrder'])

        # Adding M2M table for field coupons on 'ManuscriptOrder'
        db.create_table('swe_manuscriptorder_coupons', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manuscriptorder', models.ForeignKey(orm['swe.manuscriptorder'], null=False)),
            ('coupon', models.ForeignKey(orm['swe.coupon'], null=False))
        ))
        db.create_unique('swe_manuscriptorder_coupons', ['manuscriptorder_id', 'coupon_id'])

        # Adding model 'OriginalDocument'
        db.create_table('swe_originaldocument', (
            ('document_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['swe.Document'], unique=True, primary_key=True)),
            ('manuscriptorder', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['swe.ManuscriptOrder'], unique=True)),
        ))
        db.send_create_signal('swe', ['OriginalDocument'])

        # Adding model 'EditedDocument'
        db.create_table('swe_editeddocument', (
            ('parent_document', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['swe.Document'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('swe', ['EditedDocument'])

        # Adding model 'ManuscriptEdit'
        db.create_table('swe_manuscriptedit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manuscriptorder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.ManuscriptOrder'])),
            ('starting_document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['swe.Document'])),
            ('editeddocument', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['swe.EditedDocument'], unique=True, null=True, blank=True)),
            ('editor', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('swe', ['ManuscriptEdit'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table('swe_userprofile')

        # Deleting model 'Document'
        db.delete_table('swe_document')

        # Deleting model 'SubjectList'
        db.delete_table('swe_subjectlist')

        # Deleting model 'SubjectCategory'
        db.delete_table('swe_subjectcategory')

        # Deleting model 'Subject'
        db.delete_table('swe_subject')

        # Deleting model 'ServiceList'
        db.delete_table('swe_servicelist')

        # Deleting model 'WordCountRange'
        db.delete_table('swe_wordcountrange')

        # Deleting model 'ServiceType'
        db.delete_table('swe_servicetype')

        # Deleting model 'PricePoint'
        db.delete_table('swe_pricepoint')

        # Deleting model 'Coupon'
        db.delete_table('swe_coupon')

        # Removing M2M table for field enabled_users on 'Coupon'
        db.delete_table('swe_coupon_enabled_users')

        # Deleting model 'ManuscriptOrder'
        db.delete_table('swe_manuscriptorder')

        # Removing M2M table for field coupons on 'ManuscriptOrder'
        db.delete_table('swe_manuscriptorder_coupons')

        # Deleting model 'OriginalDocument'
        db.delete_table('swe_originaldocument')

        # Deleting model 'EditedDocument'
        db.delete_table('swe_editeddocument')

        # Deleting model 'ManuscriptEdit'
        db.delete_table('swe_manuscriptedit')


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