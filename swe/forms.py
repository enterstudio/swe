import base64
import datetime
import hmac
import sha
import simplejson
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.safestring import mark_safe
from swe import models


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        )
    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        )
    email = forms.EmailField(
        label='Email address', 
        max_length = 30,
        )
    password = forms.CharField(
        label='Password',
        max_length = 30,
        widget=forms.PasswordInput,
        )
    password_confirm = forms.CharField(
        label='Password again',
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
        # email doubles as auth.models.User.username and swe.models.UserProfile.active_email. Verify that it is unique in both fields.
        # TODO make email usage consistent, allow for email change. Never use auth email
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
    email = forms.CharField(
        label='Email address', 
        max_length=30,
        )
    password = forms.CharField(
        label='Password', 
        max_length=30, 
        widget=forms.PasswordInput,
        )


class RequestResetPasswordForm(forms.Form):
    email = forms.CharField(
        label='Email address', 
        max_length=30,
        )


class ResetPasswordForm(forms.Form):
    resetpassword_key = forms.CharField(
        widget=forms.HiddenInput, 
        max_length=40,
        )
    email = forms.EmailField(
        label='Email address', 
        max_length = 30,
        )
    password = forms.CharField(
        label='New password',
        max_length = 30,
        widget=forms.PasswordInput,
        )
    password_confirm = forms.CharField(
        label='Password again',
        max_length = 30,
        widget=forms.PasswordInput,
        )


    def clean(self):
        cleaned_data = super(ResetPasswordForm,self).clean()
        if cleaned_data.get('password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('The passwords do not match')
        try:
            userprofile = models.UserProfile.objects.get(resetpassword_key=cleaned_data.get('resetpassword_key'))
        except models.UserProfile.DoesNotExist:
            raise forms.ValidationError('This request is not valid. Please submit a new request to reset your password.')
        if userprofile.resetpassword_expires < datetime.datetime.utcnow().replace(tzinfo=timezone.utc):
            raise forms.ValidationError('This request has expired. Please submit a new request to reset your password.')
        if userprofile.user.email != cleaned_data.get('email'):
            raise forms.ValidationError(
                'This request is not valid for the email address provied. '+
                'Please correct the email address or submit a new request to reset your password.')
        return cleaned_data


class ChangePasswordForm(forms.Form):    
    old_password = forms.CharField(
        label='Old password',
        max_length = 30,
        widget=forms.PasswordInput,
        )
    new_password = forms.CharField(
        label='New password',
        max_length = 30,
        widget=forms.PasswordInput,
        )
    password_confirm = forms.CharField(
        label='New password again',
        max_length = 30,
        widget=forms.PasswordInput,
        )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ChangePasswordForm,self).clean()
        if cleaned_data.get('new_password') != cleaned_data.get('password_confirm'):
            raise forms.ValidationError('The passwords do not match')
        if not self.user.check_password(cleaned_data.get('old_password')):
            raise forms.ValidationError('The password is incorrect')
        return cleaned_data


class ConfirmForm(forms.Form):
    activation_key = forms.CharField(
        label='Activation Key', 
        max_length=40,
        widget=forms.HiddenInput,
        )


class ActivationRequestForm(forms.Form):
    email = forms.CharField(
        label='Email address',
        max_length=30,
        )

    def clean_email(self):
        #TODO: Fix this to avoid revealing if an email is registered.
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


class OrderForm(forms.Form):
    title = forms.CharField(label='Title (choose any name that helps you remember)', max_length=50, required=False)
    subject = forms.ChoiceField(
        label='Field of study', 
        choices=models.SubjectList.objects.get(is_active=True).get_subject_choicelist(), 
        )
    word_count = forms.ChoiceField(
        label='Word count (do not include references)',
        choices=models.ServiceList.objects.get(is_active=True).get_wordcountrange_choicelist(),
        )


class SelectServiceForm(forms.Form):
    invoice_id = None
    servicetype = forms.ChoiceField(label='Type of service')
    word_count_exact = forms.IntegerField(label = 'Number of words in the manuscript (excluding references)')
    def __init__(self, *args, **kwargs):
        # Invoice_id must be in kwargs
        try:
            self.invoice_id = kwargs['invoice_id']
            del[kwargs['invoice_id']]
        except KeyError:
            raise Exception('Missing required argument invoice_id.')
        super(SelectServiceForm, self).__init__(*args, **kwargs)
        manuscriptorder = models.ManuscriptOrder.objects.get(invoice_id=self.invoice_id)
        self.fields[u'servicetype'].choices = manuscriptorder.wordcountrange.get_pricepoint_choicelist()
        if manuscriptorder.wordcountrange.max_words is not None:
            # A definite word count range is already specified. Drop the field.
            del(self.fields['word_count_exact'])
            
    def clean_word_count_exact(self):
        manuscriptorder = models.ManuscriptOrder.objects.get(invoice_id=self.invoice_id)
        maximum_allowed = 1000000
        words = self.cleaned_data[u'word_count_exact']
        if manuscriptorder.wordcountrange.min_words is not None:
            if words < manuscriptorder.wordcountrange.min_words:            
                raise forms.ValidationError("This word count is not in the selected range.")
        if manuscriptorder.wordcountrange.max_words is not None:
            if words > manuscriptorder.wordcountrange.max_words:            
                raise forms.ValidationError("This word count is not in the selected range.")
        if words > maximum_allowed:
            raise forms.ValidationError("Please contact support submit a document of this length.")
        return words


class SubmitOrderFreeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # invoice_id must be defined in kwargs
        super(SubmitOrderFreeForm, self).__init__(*args, **kwargs)


class S3UploadForm(forms.Form):
    """
    http://developer.amazonwebservices.com/connect/entry.jspa?externalID=1434

    <input type="hidden" name="key" value="uploads/${filename}">
    <input type="hidden" name="AWSAccessKeyId" value="YOUR_AWS_ACCESS_KEY"> 
    <input type="hidden" name="acl" value="private"> 
    <input type="hidden" name="success_action_redirect" value="http://localhost/">
    <input type="hidden" name="policy" value="YOUR_POLICY_DOCUMENT_BASE64_ENCODED">
    <input type="hidden" name="signature" value="YOUR_CALCULATED_SIGNATURE">
    """
    key = forms.CharField(widget = forms.HiddenInput)
    AWSAccessKeyId = forms.CharField(widget = forms.HiddenInput)
    acl = forms.CharField(widget = forms.HiddenInput)
    success_action_redirect = forms.CharField(widget = forms.HiddenInput)
    policy = forms.CharField(widget = forms.HiddenInput)
    signature = forms.CharField(widget = forms.HiddenInput)
    file = forms.FileField(widget = forms.FileInput(attrs={'class':'fileinput'}))
    
    def __init__(self, aws_access_key, aws_secret_key, bucket, key,
                 expires_after = datetime.timedelta(days = 1),
                 acl = 'private',
                 success_action_redirect = None,
                 min_size = 0,
                 max_size = None,
                 ):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.bucket = bucket
        self.key = key
        self.expires_after = expires_after
        self.acl = acl
        self.success_action_redirect = success_action_redirect
        self.min_size = min_size
        self.max_size = max_size
        
        policy = base64.b64encode(self.calculate_policy())
        signature = self.sign_policy(policy)
        
        initial = {
            'key': self.key,
            'AWSAccessKeyId': self.aws_access_key,            
            'acl': self.acl,
            'policy': policy,
            'signature': signature,
        }
        if self.success_action_redirect:
            initial['success_action_redirect'] = self.success_action_redirect
        
        super(S3UploadForm, self).__init__(initial = initial)
        
        if self.max_size:
            self.fields['MAX_SIZE'] = forms.CharField(widget=forms.HiddenInput)
            self.initial['MAX_SIZE'] = self.max_size
        
        # Don't show success_action_redirect if it's not being used
        if not self.success_action_redirect:
            del self.fields['success_action_redirect']

    def add_prefix(self, field_name):
        # Hack to use the S3 required field name
        if field_name == 'content_type' and self.content_type:
            field_name = 'Content-Type'
        return super(S3UploadForm, self).add_prefix(field_name)

    def as_html(self):
        """
        Use this instead of as_table etc, because S3 requires the file field
        come AFTER the hidden fields, but Django's normal form display methods
        position the visible fields BEFORE the hidden fields.
        """
        html = ''.join(map(unicode, self.hidden_fields()))
        html += unicode(self['file'])
        return html
    
    def as_form_html(self, prefix='', suffix=''):
        html = """
        <form action="%s" method="post" enctype="multipart/form-data">
        <p>%s <input type="submit" value="Upload"></p>
        </form>
        """.strip() % (self.action(), self.as_html())
        return html
    
    def is_multipart(self):
        return True
    
    def action(self):
        return 'https://%s.s3.amazonaws.com/' % self.bucket
    
    def calculate_policy(self):
        conditions = [
            {'bucket': self.bucket},
            {'acl': self.acl},
            ['starts-with', '$key', self.key.replace('${filename}', '')],
        ]
        if self.max_size:
            conditions.append(
                ['content-length-range',self.min_size,self.max_size]
            )
        if self.success_action_redirect:
            conditions.append(
                {'success_action_redirect': self.success_action_redirect},
            )
        
        policy_document = {
            "expiration": (
                datetime.datetime.now() + self.expires_after
            ).isoformat().split('.')[0] + 'Z',
            "conditions": conditions,
        }
        return simplejson.dumps(policy_document, indent=2)
    
    def sign_policy(self, policy):
        return base64.b64encode(
            hmac.new(self.aws_secret_key, policy, sha).digest()
        )
