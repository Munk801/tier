from django.db import models
import datetime

class ContactForm(models.Model):
	name = models.CharField(max_length=150)
	email = models.EmailField(max_length=250)
	topic = models.CharField(max_length=200)
	timestamp = models.DateTimeField(
		auto_now_add=True,
		default=datetime.datetime.now
	)

	def __unicode(self):
		return self.email

	class Meta:
		ordering = ['-timestamp']

