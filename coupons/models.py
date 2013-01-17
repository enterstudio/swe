import datetime
from decimal import Decimal, ROUND_UP
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def nearest_cent(x):
    return Decimal(x).quantize(Decimal('1.00'), rounding=ROUND_UP)


class EmailDomain(models.Model):
    domain = models.CharField(max_length=30)

    def __unicode__(self):
        return self.domain


class Referral(models.Model):
    referred_user = models.ForeignKey(User, null=True, blank=True, related_name='has_been_referred')
    referred_email = models.CharField(max_length=100, null=True, blank=True)
    referred_by = models.ForeignKey(User, null=True, blank=True, related_name='has_made_referral')
    reffered_by_email = models.CharField(max_length=100, null=True, blank=True)
    is_activated = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s referred %s' % (self.referred_by_email, self.new_user)


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
    promotional_code = models.CharField(max_length=20, null=True, blank=True)
    # discount amount
    dollars_off = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)
    is_by_percent = models.BooleanField()
    percentoff = models.IntegerField(null=True, blank=True)
    # validity limits
    expiration_date = models.DateTimeField() #applies when claiming, not when redeeming
    default_use_by_date = models.DateTimeField(null=True, blank=True, default=None)
    default_use_by_days = models.FloatField(null=True, blank=True, default=None)
    userfilters = models.ManyToManyField(UserFilter, null=True, blank=True)
    multiple_use_allowed = models.BooleanField(default=False)
    persists_after_use = models.BooleanField(default=False)

    def is_available_to_user(self, user):
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        if self.expiration_date < now:
            return False
        if self.is_claimed_by_user(user):
            # Duplicate claim
            return False
        # TODO does it pass the user filters?           
        return True

    def is_claimed_by_user(self, user):
        claims = user.discountclaim_set.all()
        for i in range(claims.count()):
            if self.pk == claims[i].discount.pk:
                return claims[i]
        return False

    def claim_discount(self, user):
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        c = DiscountClaim(
            discount=self,
            customer=user,
            date_claimed=now,
        )
        if self.default_use_by_date:
            c.use_by_date = self.default_use_by_date
        elif self.default_use_by_days:
            c.use_by_date = now + datetime.timedelta(days=self.default_use_by_days)
        c.save()
        return c

    def get_dollars_off(self, full_price):
        if self.is_by_percent:
            return nearest_cent(float(full_price) * float(self.percentoff) / 100.0)
        else:
            return nearest_cent(self.dollars_off)

    def __unicode__(self):
        return self.display_text


class DiscountClaim(models.Model):
    discount = models.ForeignKey(Discount)
    customer = models.ForeignKey(User)
    date_claimed = models.DateTimeField()
    date_used = models.DateTimeField(null=True, blank=True)
    use_by_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.discount


class FeaturedDiscount(models.Model):
    discount = models.ForeignKey(Discount)
    promotional_text = models.CharField(max_length=200, null=True, blank=True)
    offer_begins = models.DateTimeField()
    offer_ends = models.DateTimeField()
    
    def __unicode__(self):
        return '%s' % self.discount
