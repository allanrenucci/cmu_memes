from django.shortcuts import render, redirect, get_object_or_404

# Decorator require_POST
from django.views.decorators.http import require_POST

# Decorator transaction.atomic
from django.db import transaction

# Create and log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

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

@login_required
def profile(request):
	context = {}
	user = request.user

	context['password_form'] = PasswordForm()
	context['profile_form'] = ProfileForm(instance=user)
	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
def set_password(request):
	context = {}
	user = request.user

	form = PasswordForm(user.username, request.POST)

	if form.is_valid():
		pwd = form.cleaned_data['new_password']
		user.set_password(pwd)
		user.save()
		context['password_form'] = PasswordForm()
		context['infos'] = ["Password successfully changed!"]
	else:
		context['password_form'] = form

	context['profile_form'] = ProfileForm(instance=user)
	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
def update_profile(request):
	context = {}
	user = request.user

	form = ProfileForm(request.POST, instance=user)

	if form.is_valid():
		form.save()
		context['profile_form'] = ProfileForm(instance=user)
		context['infos'] = ["Profile successfully updated!"]
	else:
		context['profile_form'] = form
	
	context['password_form'] = PasswordForm()
	return render(request, 'registration/profile.html', context)

@login_required
def delete_profile(request):
	request.user.delete()
	return redirect('home')