from django.shortcuts import render, redirect, get_object_or_404

# transaction.atomic decorator
from django.db import transaction

# create and log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from models import *
from forms import *

def home(request):
	return render(request, 'website/index.html')


@transaction.atomic
def register(request):
	context = {}

	# Just display the registration form if this is a GET request
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'registration/register.html', context)

	new_user = User()
	form = RegistrationForm(request.POST, instance=new_user)

	# Checks the validity of the form data
	if not form.is_valid():
		context['form'] = form
		return render(request, 'registration/register.html', context)

	# Hack to hash password
	password = new_user.password
	new_user.set_password(password)
	form.save()

	new_user = authenticate(username=new_user.username, password=password)
	login(request, new_user)
	return redirect('home')
