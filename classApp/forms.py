from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models	import User
from django.core.exceptions import ValidationError
from .models import Profile, GroupEvent, College, Major, FeedChat, Course, StudyGroup, GroupPost

class UserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields =['first_name','last_name','email']

class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['profile_pic','bio','college','major','classification']

class ClassesForm(forms.ModelForm):
	classes = forms.ModelMultipleChoiceField(
		queryset=Course.objects.all().order_by('name'),
		widget=forms.CheckboxSelectMultiple(),
		required=False,
		label="Select your classes (optional)"
	)
	
	class Meta:
		model = Profile
		fields = ['classes']

class GroupEventForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUES', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THUR', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    meeting_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Meeting Days"
    )

    class Meta:
        model = GroupEvent
        fields = [
            'title',
            'description',
            'session_start_date',
            'session_end_date',
            'meeting_days',
            'session_start_time',
            'session_end_time',
            'location',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Session title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "What will this study session cover?"
            }),
            'session_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'session_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'session_start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'session_end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Library, Zoom, classroom, etc.'
            }),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.meeting_days:
            self.fields['meeting_days'].initial = self.instance.meeting_days.split(',')

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('session_start_date')
        end_date = cleaned_data.get('session_end_date')
        start_time = cleaned_data.get('session_start_time')
        end_time = cleaned_data.get('session_end_time')
        meeting_days = cleaned_data.get('meeting_days')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be after the start date.")

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after the start time.")

        if not meeting_days:
            raise forms.ValidationError("Select at least one meeting day.")

        return cleaned_data

class CustomRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    classification = forms.ChoiceField(
        choices=Profile.YEAR_IN_SCHOOL_CHOICES,
        required=True,
        label="Year in School"
    )
    college = forms.ModelChoiceField(queryset=College.objects.all(), required=True)
    major = forms.ModelChoiceField(queryset=Major.objects.none(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Repopulate major queryset if form is submitted or has data
        if 'college' in self.data and 'classification' in self.data:
            try:
                college_id = int(self.data.get('college'))
                classification = self.data.get('classification')
                is_graduate = (classification == 'GR' or classification == 'PD')
                self.fields['major'].queryset = Major.objects.filter(
                    college_id=college_id,
                    is_graduate=is_graduate
                )
            except (ValueError, TypeError):
                pass

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not email.endswith('@utrgv.edu'):
            raise ValidationError("You must use a @utrgv.edu email address.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

class FeedChatForm(forms.ModelForm):
    class Meta:
        model = FeedChat
        fields = ['content', 'resource_file', 'resource_title', 'resource_file_type']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "What's on your mind? Share with your study group..."
            }),
            'resource_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resource title (optional)'
            }),
            'resource_file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'File type (optional, e.g. pdf, docx, pptx)'
            }),
        }
        labels = {
            'content': '',
            'resource_file': '',
            'resource_title': '',
            'resource_file_type': '',
        }

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        resource_file = cleaned_data.get('resource_file')

        if not content and not resource_file:
            raise forms.ValidationError("Add text or upload a resource.")
        return cleaned_data

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['course_code', 'course_subject', 'name', 'description', 'icon_color']
        
class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['content', 'resource_file', 'resource_title', 'resource_file_type']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control border-0 bg-transparent',
                'rows': 3,
                'placeholder': "What's on your mind? Share with your study group..."
            }),
            'resource_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resource title (optional)'
            }),
            'resource_file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'File type (optional, e.g. pdf, docx, pptx)'
            }),
        }
        labels = {
            'content': '',
            'resource_file': '',
            'resource_title': '',
            'resource_file_type': '',
        }

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        resource_file = cleaned_data.get('resource_file')

        if not content and not resource_file:
            raise forms.ValidationError("Add text or upload a resource.")
        return cleaned_data