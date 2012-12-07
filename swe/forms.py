from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from swe.models import SubjectList, Subject, ServiceList, ServiceType, WordCountRange, ManuscriptOrder
 
class RegisterForm(forms.Form):
    first_name = forms.CharField(label='First Name',
                            max_length=30,
                            )
    last_name = forms.CharField(label='Last Name',
                            max_length=30,
                            )
    #email is be treated as username in auth.models.User and separately written to active_email in UserProfile
    email = forms.EmailField(label='Email address', 
                            max_length = 30,
                            )
    password = forms.CharField(label='Password',
                            max_length = 30,
                            widget=forms.PasswordInput,
                            )
    password_confirm = forms.CharField(label='Re-type password',
                            max_length = 30,
                            widget=forms.PasswordInput,
                            )

    def clean(self):
        cleaned_data = super(RegisterForm,self).clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('The passwords do not match')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']

        # email doubles used as username. Verify that it is unique in both fields.
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                User.objects.get(username=email)
            except User.DoesNotExist:
                return email

        raise forms.ValidationError("This email address is already registered.")
        return email

class LoginForm(forms.Form):
    email = forms.CharField(label='Email address',max_length=30)
    password = forms.CharField(label='Password', max_length=30, widget=forms.PasswordInput)

class ConfirmForm(forms.Form):
    activation_key = forms.CharField(label='Activation Key', max_length=100)

class ActivationRequestForm(forms.Form):
    email = forms.CharField(label='Email address',max_length=30)

    def clean_email(self):
        email = self.cleaned_data['email']

        # Verify that email is on record.
        try:
            u = User.objects.get(username=email)
            # Verify that account is not already active.
            if u.is_active:
                raise forms.ValidationError("This account has already been activated.")
        except User.DoesNotExist:
            raise forms.ValidationError("This email address is not registered.")

        return email


class UploadManuscriptForm(forms.Form):
    step = forms.IntegerField(initial=1, widget = forms.widgets.HiddenInput())
    title = forms.CharField(label='Title (choose any name that helps you remember)', max_length=50, required=False)
    subject = forms.ChoiceField(
        label='Field of study', 
        choices=SubjectList.objects.get(is_active=True).get_subject_choicelist(), 
        )
    word_count = forms.ChoiceField(
        label='Word count (do not include references)',
        choices=ServiceList.objects.get(is_active=True).get_wordcountrange_choicelist(),
        )
    manuscript_file = forms.FileField(label='Select your manuscript file')

class SelectServiceForm(forms.Form):
    servicetype = forms.ChoiceField(label='Type of service')
    def __init__(self, *args, **kwargs):
        # Order PK must be defined either in kwargs or POST data
        try:
            order_pk = kwargs['order_pk']
            del[kwargs['order_pk']]
        except KeyError:
            order_pk = None
        super(SelectServiceForm, self).__init__(*args, **kwargs)
        self.fields['step'] = forms.IntegerField(widget = forms.widgets.HiddenInput(), initial=2)
        if order_pk == None:
            try:
                order_pk = self.data['order']
            except KeyError:
                raise Exception('Order number is not available.')
        self.fields['order'] = forms.IntegerField(widget = forms.widgets.HiddenInput(), initial=order_pk)
        self.fields['servicetype'].choices = ManuscriptOrder.objects.get(pk=order_pk).wordcountrange.get_pricepoint_choicelist()

class SelectServiceAndExactWordCountForm(SelectServiceForm):
    def __init__(self, *args, **kwargs):
        super(SelectServiceAndExactWordCountForm, self).__init__(*args, **kwargs)
        self.fields['step'] = forms.IntegerField(widget = forms.widgets.HiddenInput(), initial=3)
        self.fields['word_count_exact'] = forms.IntegerField(label = 'Number of words in the manuscript (excluding references)')
