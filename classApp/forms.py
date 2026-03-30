from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models	import User
from django.core.exceptions import ValidationError
from .models import Profile, GroupEvent, College, Major

class UserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields =['first_name','last_name','email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['profile_pic','bio','college','major']

class GroupEventForm(forms.ModelForm):
	class Meta:
		model = GroupEvent
		fields = ['title', 'date', 'location', 'attendees']
		widgets = {
			# This allows you to select multiple users at once 
			'attendees': forms.CheckboxSelectMultiple(),
		}

class CustomRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    college = forms.ModelChoiceField(queryset=College.objects.all(), required=True)
    major = forms.ModelChoiceField(queryset=Major.objects.none(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Repopulate major queryset if form is submitted or has data
        if 'college' in self.data:
            try:
                college_id = int(self.data.get('college'))
                self.fields['major'].queryset = Major.objects.filter(college_id=college_id)
            except (ValueError, TypeError):
                pass

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not email.endswith('@utrgv.edu'):
            raise ValidationError("You must use a @utrgv.edu email address.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email