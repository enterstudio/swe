"""
Tests for views and forms
"""

from django.test import TestCase
from swe.management.commands import activate_subjects, activate_services
from swe.models import UserProfile, User

class AnonymousViews(TestCase):
    """
    Test all views as a user not logged in
    Minimal testing, GET each page and check content
    """
    def setUp(self):
        activate_subjects.Command().handle()
        activate_services.Command().handle()

    def test_home_page(self):
        response = self.client.get('/home/')
        self.assertContains(response, 'Professional editing services') # Banner content
        self.assertContains(response, "<a href='/login/'>") # Login and sign up links only if logged out
        self.assertContains(response, "<a href='/register/'>")
        self.assertNotContains(response, 'action="/logout/"') # Logout and account links only if logged in
        self.assertNotContains(response, "<a href='/account/'>")
        self.assertContains(response, '<a href="/order/">') # Menu bar
        self.assertContains(response, '<a href="/terms/">Terms of service</a>') # Footer
        self.assertContains(response, '&copy') # Copyright
        
class AuthenticatedViews(TestCase):
    """
    Test all views as an authenticated user
    Minimal testing, GET each page and check content
    """
    email = 'test@sciencewritingexperts.com'
    password = 'p4s$w0rd'
    
    def setUp(self):
        activate_subjects.Command().handle()
        activate_services.Command().handle()

        self.user = UserProfile.create_user_and_profile(
            email=self.email,
            password=self.password,
            first_name='John', 
            last_name='Doe'
            )

        self.user.user.is_active=True
        self.user.user.save()

        success = self.client.login(username=self.email, password=self.password)
        self.assertTrue(success, 'Login failed')

    def test_home_page(self):
        response = self.client.get('/home/')

        self.assertContains(response, 'Professional editing services') # Banner content
        self.assertContains(response, 'action="/logout/"') # Logout and account links only if logged in
        self.assertContains(response, "<a href='/account/'>")
        self.assertNotContains(response, "<a href='/login/'>") # Login and sign up links only if logged out
        self.assertNotContains(response, "<a href='/register/'>")
        self.assertContains(response, '<a href="/order/">') # Menu bar
        self.assertContains(response, '<a href="/terms/">Terms of service</a>') # Footer
        self.assertContains(response, '&copy') # Copyright
