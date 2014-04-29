from django.shortcuts import render, redirect, get_object_or_404

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

def about(request):
	return render(request, 'website/about.html')

def home(request):
	context = {}
	context['memes'] = Meme.get_memes()
	context['form'] = MemeForm()
	return render(request, 'website/index.html', context)


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

	context['memes'] = Meme.get_memes(author=user)
	context['password_form'] = PasswordForm()
	context['profile_form'] = ProfileForm(instance=user)
	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
@transaction.atomic
def set_password(request):
	context = {}
	user = request.user

	form = PasswordForm(user.username, request.POST)

	if form.is_valid():
		pwd = form.cleaned_data['new_password']
		user.set_password(pwd)
		user.save()
		context['password_form'] = PasswordForm()
		context['infos'] = ['Password successfully changed!']
	else:
		context['password_form'] = form

	context['memes'] = Meme.get_memes(author=user)
	context['profile_form'] = ProfileForm(instance=user)
	return render(request, 'registration/profile.html', context)

@require_POST
@login_required
@transaction.atomic
def update_profile(request):
	context = {}
	user = request.user

	form = ProfileForm(request.POST, instance=user)

	if form.is_valid():
		form.save()
		context['profile_form'] = ProfileForm(instance=user)
		context['infos'] = ['Profile successfully updated!']
	else:
		context['profile_form'] = form
	
	context['memes'] = Meme.get_memes(author=user)
	context['password_form'] = PasswordForm()
	return render(request, 'registration/profile.html', context)

@login_required
@transaction.atomic
def delete_profile(request):
	context = {}
	request.user.delete()
	logout(request)
	context['memes'] = Meme.get_memes()
	context['infos'] = ['Your account was successfully deleted!']
	return render(request, 'website/index.html', context)

@require_POST
@login_required
@transaction.atomic
def post_meme(request):
	context = {}
	new_meme = Meme(author=request.user)
	form = MemeForm(request.POST, request.FILES, instance=new_meme)

	if form.is_valid():
		form.save()
		form = MemeForm()

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
	data = {}
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

	data['up_vote'] = meme.up_vote_count
	data['down_vote'] = meme.down_vote_count
	content = json.dumps(data)
	content_type = "application/json"
	return StreamingHttpResponse(content, content_type=content_type)

@login_required
@transaction.atomic
def meme_downvote(request, id):
	data = {}
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

	data['up_vote'] = meme.up_vote_count
	data['down_vote'] = meme.down_vote_count
	content = json.dumps(data)
	content_type = "application/json"
	return StreamingHttpResponse(content, content_type=content_type)
