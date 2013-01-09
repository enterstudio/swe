from django.contrib import admin
from coupons.models import EmailDomain, UserFilter, Discount, DiscountClaim, FeaturedDiscount

admin.site.register([EmailDomain, UserFilter, Discount, DiscountClaim, FeaturedDiscount])


