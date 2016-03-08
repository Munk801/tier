"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.shortcuts import render_to_response
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
import django_ecommerce.settings as settings
from payments.models import User
from payments.forms import UserForm
from payments.views import soon, register

import mock

class ViewTesterMixin(object):

	@classmethod
	def setupViewTester(cls, url, view_func, expected_html, status_code=200, session={}):
		request_factory = RequestFactory()
		cls.request = request_factory.get(url)
		cls.request.session = session
		cls.status_code = status_code
		cls.url = url
		cls.view_func = staticmethod(view_func)
		cls.expected_html = expected_html

	def test_resolves_to_correct_view(self):
		test_view = resolve(self.url)
		self.assertEquals(test_view.func, self.view_func)

	def test_returns_appropriate_response_code(self):
		resp = self.view_func(self.request)
		self.assertEquals(resp.status_code, self.status_code)

	def test_returns_correct_html(self):
		resp = self.view_func(self.request)
		self.assertEquals(resp.content, self.expected_html)

class RegisterPageTests(TestCase, ViewTesterMixin):

	@classmethod
	def setUpClass(cls):
		super(RegisterPageTests, cls).setUpClass()
		html = render_to_response(
			'register.html',
			{
				'form': UserForm(),
				'months': range(1, 12),
				'publishable': settings.STRIPE_PUBLISHABLE,
				'soon': soon(),
				'user': None,
				'years': range(2011, 2036),
			}
		)
		ViewTesterMixin.setupViewTester(
			'/register',
			register,
			html.content,
		)

	def setUp(self):
		request_factory = RequestFactory()
		self.request = request_factory.get(self.url)

	def test_invalid_form_returns_registration_page(self):
		with mock.patch('payments.forms.UserForm.is_valid') as user_mock:
			user_mock.return_value = False
			self.request.method = 'POST'
			self.request.POST = None
			resp = register(self.request)
			self.assertEquals(resp.content, self.expected_html)
			self.assertEquals(user_mock.call_count, 1)

	def test_registering_new_user_returns_successfully(self):
		self.request.session = {}
		self.request.method = 'POST'
		self.request.POST = {
			'email' : 'python@rocks.com',
			'name' : 'pyRock',
			'stripe_token' : '4242424242424242',
			'last_4_digits' : '4242',
			'password' : 'bad_password',
			'ver_password' : 'bad_password',
		}
		# Create a mock of the stripe server since we
		# need to pass the data to it
		with mock.patch('stripe.Customer') as stripe_mock:
			config = {'create.return_value' : mock.Mock()}
			stripe_mock.configure_mock(**config)
			resp = register(self.request)
			self.assertEquals(resp.content, "")
			self.assertEquals(resp.status_code, 302)
			self.assertEquals(self.request.session['user'], 1)

			# Verify user was stored in db
			User.objects.get(email='python@rocks.com')



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
