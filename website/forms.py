from django import forms

from models import *
from django.contrib.auth.models import User

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