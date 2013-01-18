import datetime
from django.contrib import messages
from django.utils import timezone
import coupons


def claim_featured_discounts(request, user):
    now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    featured_discounts = coupons.models.FeaturedDiscount.objects.filter(offer_begins__lte=now).filter(offer_ends__gte=now)
    any_claimed = False
    for featured_discount in featured_discounts:
        # no message if discount claim fails, since user did not explicitly request it
        claim_discount_by_object(request, user, featured_discount.discount, fail_silent=True)


def claim_discount(request, user, promotional_code):
     try:
         discount = coupons.models.Discount.objects.get(promotional_code=promotional_code)
     except coupons.models.Discount.DoesNotExist:
         _add_message(request, messages.ERROR, 'We are sorry, but the discount "%s" is not available.' % promotional_code)
         return
     return claim_discount_by_object(request, user, discount, fail_silent=False)


def _add_message(request, msg_type, msg, fail_silent=False):
    if fail_silent and (msg_type==messages.ERROR or msg_type==messages.WARNING):
        pass
    else:
        messages.add_message(request, msg_type, msg)


def claim_discount_by_object(request, user, discount, fail_silent=False):
    if not discount.is_available_to_user(user):
        _add_message(request, messages.ERROR, 'We are sorry, but the discount "%s" has expired.' % discount.display_text, fail_silent)
        return False
    claim = discount.claim_discount(user)
    if claim.use_by_date is not None:
        valid_thru = 'valid through %s' % claim.use_by_date.strftime("%Y-%m-%d")
    else:
        valid_thru = ''
    _add_message(request, messages.SUCCESS, 
                 ('Congratulations! You have claimed the following discount: "%s" '+valid_thru+'.') % discount.display_text)
    return claim

def get_discounts_claimed_by_user(user):
    return user.discountclaim_set.all()

def get_active_discounts_claimed_by_user(user):
    return get_discounts_claimed_by_user(user).filter(date_used=None)

def check_for_promotion(request):
    now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    return coupons.models.FeaturedDiscount.objects.filter(offer_begins__lt=now).filter(offer_ends__gt=now)
