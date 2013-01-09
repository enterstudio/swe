# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailDomain'
        db.create_table('coupons_emaildomain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('coupons', ['EmailDomain'])

        # Adding model 'UserFilter'
        db.create_table('coupons_userfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('registered_before_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('registered_after_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal('coupons', ['UserFilter'])

        # Adding M2M table for field email_domains on 'UserFilter'
        db.create_table('coupons_userfilter_email_domains', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userfilter', models.ForeignKey(orm['coupons.userfilter'], null=False)),
            ('emaildomain', models.ForeignKey(orm['coupons.emaildomain'], null=False))
        ))
        db.create_unique('coupons_userfilter_email_domains', ['userfilter_id', 'emaildomain_id'])

        # Adding model 'Discount'
        db.create_table('coupons_discount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('coupon_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('dollars_off', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=7, decimal_places=2)),
            ('is_by_percent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('percentoff', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('default_use_by_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('coupons', ['Discount'])

        # Adding M2M table for field userfilters on 'Discount'
        db.create_table('coupons_discount_userfilters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('discount', models.ForeignKey(orm['coupons.discount'], null=False)),
            ('userfilter', models.ForeignKey(orm['coupons.userfilter'], null=False))
        ))
        db.create_unique('coupons_discount_userfilters', ['discount_id', 'userfilter_id'])

        # Adding model 'DiscountClaim'
        db.create_table('coupons_discountclaim', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discount', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coupons.Discount'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date_claimed', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_used', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('use_by_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('number_of_times_allowed', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('number_of_times_used', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('coupons', ['DiscountClaim'])

        # Adding model 'FeaturedDiscount'
        db.create_table('coupons_featureddiscount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('discount', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coupons.Discount'])),
            ('offer_begins', self.gf('django.db.models.fields.DateTimeField')()),
            ('offer_ends', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('coupons', ['FeaturedDiscount'])


    def backwards(self, orm):
        # Deleting model 'EmailDomain'
        db.delete_table('coupons_emaildomain')

        # Deleting model 'UserFilter'
        db.delete_table('coupons_userfilter')

        # Removing M2M table for field email_domains on 'UserFilter'
        db.delete_table('coupons_userfilter_email_domains')

        # Deleting model 'Discount'
        db.delete_table('coupons_discount')

        # Removing M2M table for field userfilters on 'Discount'
        db.delete_table('coupons_discount_userfilters')

        # Deleting model 'DiscountClaim'
        db.delete_table('coupons_discountclaim')

        # Deleting model 'FeaturedDiscount'
        db.delete_table('coupons_featureddiscount')


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
        'coupons.discount': {
            'Meta': {'object_name': 'Discount'},
            'coupon_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'default_use_by_time': ('django.db.models.fields.DateTimeField', [], {}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'dollars_off': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '7', 'decimal_places': '2'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_by_percent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'percentoff': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'userfilters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coupons.UserFilter']", 'symmetrical': 'False'})
        },
        'coupons.discountclaim': {
            'Meta': {'object_name': 'DiscountClaim'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'date_claimed': ('django.db.models.fields.DateTimeField', [], {}),
            'date_used': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coupons.Discount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_of_times_allowed': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'number_of_times_used': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'use_by_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'coupons.emaildomain': {
            'Meta': {'object_name': 'EmailDomain'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'coupons.featureddiscount': {
            'Meta': {'object_name': 'FeaturedDiscount'},
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coupons.Discount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer_begins': ('django.db.models.fields.DateTimeField', [], {}),
            'offer_ends': ('django.db.models.fields.DateTimeField', [], {})
        },
        'coupons.userfilter': {
            'Meta': {'object_name': 'UserFilter'},
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email_domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coupons.EmailDomain']", 'null': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registered_after_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'registered_before_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        }
    }

    complete_apps = ['coupons']