"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve
from .views import index

class MainPageTests(TestCase):

	@classmethod
	def setUpClass(cls):
		super(MainPageTests, cls).setUpClass()
		request_factory = RequestFactory()
		cls.request = request_factory.get('/')
		cls.request.session = {}

	def test_root_resolves_to_main_view(self):
		main_page = resolve('/')
		self.assertEqual(main_page.func, index)

