from django import forms

from models import *
from django.contrib.auth.models import User

from django.contrib.auth import authenticate

class RegistrationForm(forms.ModelForm):

	confirm_password = forms.CharField(
		max_length=200,
		widget=forms.PasswordInput)

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		self.fields['email'].required = True

	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password']
		widgets = {
			'password': forms.PasswordInput
		}

	def clean(self):
		cleaned_data = super(RegistrationForm, self).clean()
		pwd = cleaned_data.get('password')
		pwd_conf = cleaned_data.get('confirm_password')

		if pwd and pwd_conf and pwd != pwd_conf:
			raise forms.ValidationError("Password did not match.")

		return cleaned_data
	
	
	def clean_username(self):
		username = self.cleaned_data.get('username')

		if User.objects.filter(username=username):
			raise forms.ValidationError("Username is already taken")

		return username

class ProfileForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)
		self.fields['email'].required = True
		
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
	
class PasswordForm(forms.Form):
	old_password = forms.CharField(max_length=200, widget=forms.PasswordInput)
	new_password = forms.CharField(max_length=200, widget=forms.PasswordInput)
	confirm_password = forms.CharField(max_length=200,
		widget=forms.PasswordInput)

	def __init__(self, user=None, *args, **kwargs):
		self.user = user
		super(PasswordForm, self).__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super(PasswordForm, self).clean()
		pwd = cleaned_data.get('new_password')
		pwd_conf = cleaned_data.get('confirm_password')

		if pwd and pwd_conf and pwd != pwd_conf:
			raise forms.ValidationError("Password did not match.")

		return cleaned_data

	def clean_old_password(self):
		pwd = self.cleaned_data.get('old_password')
		user = authenticate(username=self.user, password=pwd)

		if user is None:
			raise forms.ValidationError("Invalid Password")

		return pwd

class MemeForm(forms.ModelForm):
	class Meta:
		model = Meme
		fields = ['title', 'picture']

	