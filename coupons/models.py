from django.contrib.auth.models import User
from django.db import models


class EmailDomain(models.Model):
    domain = models.CharField(max_length=30)

    def __unicode__(self):
        return self.domain


class UserFilter(models.Model):
    description = models.CharField(max_length=100)
    email_domains = models.ManyToManyField(EmailDomain, null=True, blank=True)
    registered_before_date = models.DateTimeField(null=True, blank=True)
    registered_after_date = models.DateTimeField(null=True, blank=True)
    country_code = models.CharField(null=True, blank=True, max_length=2)

    def __unicode__(self):
        return self.description


class Discount(models.Model):
    display_text = models.CharField(max_length=200)
    coupon_code = models.CharField(max_length=20, null=True, blank=True)
    # discount amount
    dollars_off = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)
    is_by_percent = models.BooleanField()
    percentoff = models.IntegerField(null=True, blank=True)
    # validity limits
    expiration_date = models.DateTimeField() #applies when claiming, not when redeeming
    default_use_by_date = models.DateTimeField(null=True, blank=True, default=None)
    default_use_by_timedelta = models.DateTimeField(null=True, blank=True, default=None)
    userfilters = models.ManyToManyField(UserFilter, null=True, blank=True)

    def __unicode__(self):
        return self.display_text


class DiscountClaim(models.Model):
    discount = models.ForeignKey(Discount)
    customer = models.ForeignKey(User)
    date_claimed = models.DateTimeField()
    date_used = models.DateTimeField(null=True, blank=True)
    use_by_date = models.DateTimeField(null=True, blank=True)
    multiple_use_allowed = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s' % self.discount


class FeaturedDiscount(models.Model):
    discount = models.ForeignKey(Discount)
    offer_begins = models.DateTimeField()
    offer_ends = models.DateTimeField()
    
    def __unicode__(self):
        return self.discount
