from django.shortcuts import render, redirect, get_object_or_404

# Need to send notifications
from django.contrib import messages

# Needed to use reverse
from django.core.urlresolvers import reverse

# Decorator require_POST
from django.views.decorators.http import require_POST

# Needed to manually create HttpResponses or raise an Http404 exception
from django.http import StreamingHttpResponse, Http404

# Convert data to json format
import json

# Decorator transaction.atomic
from django.db import transaction

# Create and log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

from models import *
from forms import *

@login_required
def home(request):
	return redirect('new')

@login_required
def new(request):
	context = {}
	context['active'] = 'new'
	context['memes'] =  Meme.get_memes(order='-date')
	context['form'] = MemeForm(initial={'next': reverse('new')})

	return render(request, 'website/index.html', context)

@login_required
def best(request):
	context = {}
	context['active'] = 'best'
	context['memes'] =  Meme.get_memes(order='-up_vote_count')
	context['form'] = MemeForm(initial={'next': reverse('best')})

	return render(request, 'website/index.html', context)

def about(request):
	context = { 'active': 'about' }
	return render(request, 'website/about.html', context)


@transaction.atomic
def register(request):
	# Just display the registration form if this is a GET request
	if request.method == 'GET':
		context = {}
		context['active'] = 'register'
		context['form'] = RegistrationForm()
		return render(request, 'registration/register.html', context)

	new_user = User()
	form = RegistrationForm(request.POST, instance=new_user)

	if form.is_valid():
		# Hack to hash password
		password = new_user.password
		new_user.set_password(password)
		form.save()
		messages.success(request, 'Account successfully created!')

		new_user = authenticate(username=new_user.username, password=password)
		login(request, new_user)
		
		return redirect('home')
		
	context = {}
	context['active'] = 'register'
	context['form'] = form

	return render(request, 'registration/register.html', context)


@login_required
def profile(request):
	user = request.user

	context = {}
	context['active'] = 'profile'
	context['memes'] = Meme.get_memes(author=user)
	context['password_form'] = PasswordForm()
	context['profile_form'] = ProfileForm(instance=user)

	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
@transaction.atomic
def set_password(request):
	user = request.user
	form = PasswordForm(user.username, request.POST)

	if form.is_valid():
		pwd = form.cleaned_data['new_password']
		user.set_password(pwd)
		user.save()
		messages.success(request, 'Password updated.')
		return redirect('profile')

	context = {}
	context['active'] = 'profile'
	context['password_form'] = form
	context['memes'] = Meme.get_memes(author=user)
	context['profile_form'] = ProfileForm(instance=user)
	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
@transaction.atomic
def update_profile(request):
	user = request.user
	form = ProfileForm(request.POST, instance=user)

	if form.is_valid():
		form.save()
		messages.success(request, 'Profile details updated.')
		return redirect('profile')

	context = {}
	context['active'] = 'profile'
	context['password_form'] = form
	context['memes'] = Meme.get_memes(author=user)
	context['profile_form'] = ProfileForm(instance=user)

	return render(request, 'registration/profile.html', context)

@login_required
@transaction.atomic
def delete_profile(request):
	request.user.delete()
	logout(request)
	messages.success(request, 'Account successfully deleted!')
	return redirect('home')

@require_POST
@login_required
@transaction.atomic
def post_meme(request):
	new_meme = Meme(author=request.user)
	form = MemeForm(request.POST, request.FILES, instance=new_meme)

	if form.is_valid():
		form.save()
		messages.success(request, 'New meme successfully posted!')
		next = form.cleaned_data['next']
		return redirect(next)

	context = {}
	context['form'] = form
	context['memes'] = Meme.get_memes()

	return render(request, 'website/index.html', context)

def get_picture(request, id):
	meme = get_object_or_404(Meme, id=id)	

	if not meme.picture:
		raise Http404

	content_type = guess_type(meme.picture.name)
	return StreamingHttpResponse(meme.picture, content_type=content_type)


@login_required
@transaction.atomic
def delete_meme(request, id):
	meme = get_object_or_404(Meme, author=request.user, id=id)
	meme.delete()
	return redirect('profile')

@login_required
@transaction.atomic
def meme_upvote(request, id):
	meme = get_object_or_404(Meme, id=id)

	vote, _ = Vote.objects.get_or_create(
		meme=meme, owner=request.user,
		defaults={'value': Vote.NONE}
	)

	if vote.value == vote.NONE:
		vote.value = Vote.UP
		meme.up_vote_count += 1

	elif vote.value == vote.UP:
		vote.value = Vote.NONE
		meme.up_vote_count -= 1

	elif vote.value == Vote.DOWN:
		vote.value = Vote.UP
		meme.up_vote_count += 1
		meme.down_vote_count -= 1

	meme.save()
	vote.save()

	data = {}
	data['up_vote'] = meme.up_vote_count
	data['down_vote'] = meme.down_vote_count
	content = json.dumps(data)
	content_type = "application/json"
	return StreamingHttpResponse(content, content_type=content_type)

@login_required
@transaction.atomic
def meme_downvote(request, id):
	meme = get_object_or_404(Meme, id=id)

	vote, _ = Vote.objects.get_or_create(
		meme=meme, owner=request.user,
		defaults={'value': Vote.NONE}
	)

	if vote.value == vote.NONE:
		vote.value = Vote.DOWN
		meme.down_vote_count += 1

	elif vote.value == vote.UP:
		vote.value = Vote.DOWN
		meme.up_vote_count -= 1
		meme.down_vote_count += 1

	elif vote.value == Vote.DOWN:
		vote.value = Vote.NONE
		meme.down_vote_count -= 1

	meme.save()
	vote.save()

	data = {}
	data['up_vote'] = meme.up_vote_count
	data['down_vote'] = meme.down_vote_count
	content = json.dumps(data)
	content_type = "application/json"
	return StreamingHttpResponse(content, content_type=content_type)
