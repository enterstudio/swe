from django import forms
from django.contrib.auth.models import User
 
class RegisterForm(forms.Form):
    firstname = forms.CharField(label='First Name',
                            max_length=30,
                            )
    lastname = forms.CharField(label='Last Name',
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
    passwordconfirm = forms.CharField(label='Re-type password',
                            max_length = 30,
                            widget=forms.PasswordInput,
                            )

    def clean(self):
        cleaned_data = super(RegisterForm,self).clean()
        if cleaned_data.get('password') != cleaned_data.get('passwordconfirm'):
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


class SubmitManuscriptForm(forms.Form):    
    from swe.models import Subject, ServiceType, WordCountRange
    title = forms.CharField(label='Title (choose any name that helps you remember)', max_length=50, required=False)
    manuscriptfile = forms.FileField(label='Select your manuscript file')
    wordcount = forms.IntegerField(label='Number of words') 
    enabledwordcountranges = WordCountRange.objects.filter(enabled=True)
    wordcountrangelist = []
    for wordcountrangeitem in enabledwordcountranges:
        wordcountrangelist.append((wordcountrangeitem.word_count_range_id,wordcountrangeitem.display_text()))
    wordcount = forms.ChoiceField(label='Word count (do not include references)', choices=wordcountrangelist, required=False, initial=3)

    enabledsubjects = Subject.objects.filter(enabled=True)
    subjectlist = []
    for subjectitem in enabledsubjects:
        subjectlist.append((subjectitem.subject_id,subjectitem.display_text))
    subject = forms.ChoiceField(label='Subject area', choices=subjectlist, required=False)

    enabledservicetypes=ServiceType.objects.filter(enabled=True)
    servicelist=[]
    for servicetype in enabledservicetypes:
        servicelist.append((servicetype.service_type_id,servicetype.display_text))
    servicetype = forms.ChoiceField(label='Select a service type',choices=servicelist)
