from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from payments.forms import SigninForm, CardForm, UserForm
from payments.models import User
import django_ecommerce.settings as settings
import stripe
import datetime

stripe.api_key = settings.STRIPE_SECRET

def soon():
	soon = datetime.date.today() + datetime.timedelta(days=30)
	return {'month' : soon.month, 'year' : soon.year}

def sign_in(request):
	user = None
	# If the input method is a post, the user has already attempted sign-in
	if request.method == 'POST':
		form = SigninForm(request.POST)
		# Seems that you should always ensure validity
		if form.is_valid():
			# Retrieve the cleaned data from the form and
			# Search for the correct user.
			results = User.objects.filter(email=form.cleaned_data['email'])
			if len(results) == 1:
				# Always check for the password
				if results[0].check_password(form.cleaned_data['password']):
					request.session['user'] = results[0].pk
					return HttpResponseRedirect('/')
				else:
					form.addError('Incorrect email address or password')
			else:
				form.addError('Incorrect email address or password')
		else:
			form = SigninForm()
		print form.non_field_errors()

		return render_to_response(
			'sign_in.html',
			{
				'form' : form,
				'user' : user
			},
			context_instance=RequestContext(request)
		)

def sign_out(request):
	""" If the user signs out, remove the session from the request. """
	del request.session['user']
	return HttpResponseRedirect('/')

def register(request):
	user = None
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			# Update based on (subscription vs one time)
			customer = stripe.Customer.create(
				email=form.cleaned_data['email'],
				description=form.cleaned_data['name'],
				card=form.cleaned_data['stripe_token'],
				plan="gold",
			)
			user = User(
				name=form.cleaned_data['name'],
				email=form.cleaned_data['email'],
				last_4_digits=form.cleaned_data['last_4_digits'],
				stripe_id=customer.id,
			)
			# Ensure encrypted password
			user.set_password(form.cleaned_data['password'])
			try:
				user.save()
			except IntegrityError:
				form.addError(user.email + ' is already a member')
			else:
				request.session['user'] = user.pk
				return HttpResponseRedirect('/')
	else:
		form = UserForm()

	return render_to_response(
		'register.html',
		{
			'form' : form,
			'months' : range(1, 12),
			'publishable' : settings.STRIPE_PUBLISHABLE,
			'soon' : soon(),
			'user' : user,
			'years' : range(2011, 2036),
		},
		context_instance=RequestContext(request)
	)

def edit(request):
	# Get the user information
	uid = request.session.get('user')
	if uid is None:
		return HttpResponseRedirect('/')
	user = User.objects.get(pk=uid)
	# Update the card form
	if request.method == 'POST':
		form = CardForm(request.POST)
		if form.is_valid():
			customer = stripe.Customer.retrieve(user.stripe_id)
			customer.card = form.cleaned_data['stripe_token']
			customer.save()

			user.last_4_digits = form.cleaned_data['last_4_digits']
			user.stripe_id = customer.id
			user.save()

			return HttpResponseRedirect('/')
	else:
		form = CardForm()

	return render_to_response(
		'edit.html',
		{
			'form' : form,
			'publishable' : settings.STRIPE_PUBLISHABLE,
			'soon' : soon(),
			'months' : range(1, 12),
			'years' : range(2011, 2036),
		},
		context_instance=RequestContext(request)
	)
