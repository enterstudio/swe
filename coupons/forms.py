from django import forms

class DiscountForm(forms.Form):
    user = None
    discount_code = forms.CharField(
        label='',
        max_length=20,
        widget=forms.TextInput(attrs={ 'placeholder': 'Discount code'}),
        )

    def __init__(self, user, *args, **kwargs):
        super(DiscountForm, self).__init__(*args, **kwargs)
        if user.discountclaim_set.count() > 0:
            self.fields[u'discounts_available'] = forms.ModelChoiceField(
                label='',
                widget=forms.RadioSelect, 
                queryset = user.discountclaim_set,
                empty_label='none',
                )
            self.fields.keyOrder = ['discounts_available', 'discount_code']

