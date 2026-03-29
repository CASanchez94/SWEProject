from django import forms
from django.contrib.auth.models	import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields =['first_name','last_name','email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['bio','college','major']

class GroupEventForm(forms.ModelForm):
	class Meta:
		model = groupEvent
		fields = ['title', 'date', 'location', 'attendees']
		widgets = {
			# This allows you to select multiple users at once 
			'attendees': forms.CheckboxSelectMultiple(),
		}