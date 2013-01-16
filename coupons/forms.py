from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
import coupons


class SelectDiscountForm(forms.Form):
    def __init__(self, user, available_claims, *args, **kwargs):
        super(SelectDiscountForm,self).__init__(*args, **kwargs)
        self.fields[u'discount'] = forms.ModelChoiceField(
            queryset=available_claims,
            )


class ClaimDiscountForm(forms.Form):
    promotional_code = forms.CharField(
        label='',
        max_length=20,
        widget=forms.TextInput(attrs={ 'placeholder': _('Promotional code')}),
        )
    user = None
    
    def __init__(self, user, *args, **kwargs):
        super(ClaimDiscountForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_promotional_code(self):
        promotional_code = self.cleaned_data[u'promotional_code']
        try:
            discount = coupons.models.Discount.objects.get(promotional_code=promotional_code)
        except coupons.models.Discount.DoesNotExist:
            raise forms.ValidationError(_("This promotional code is not available."))
        if discount.is_available_to_user(self.user):
            return promotional_code
        else:
            raise forms.ValidationError(_("This promotional code is not available."))


class RemoveDiscountForm(forms.Form):
        discount = forms.CharField( 
            widget=forms.HiddenInput,
            max_length=20,
            )
