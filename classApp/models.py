from datetime import date, timedelta

from django.db import models
from django.contrib.auth.models import User

YEAR_CHOICES = [
    ('Freshman', 'Freshman'),
    ('Sophomore', 'Sophomore'),
    ('Junior', 'Junior'),
    ('Senior', 'Senior'),
    ('Graduate', 'Graduate'),
]

class College(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Major(models.Model):

    name = models.CharField(max_length=255)
    # Allows only majors from specific college
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="majors")
    is_graduate = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    name = models.CharField(max_length=15) # 12 Characters for course code (e.g. CSCI XXXX-XX) + 3 just in case lol

    def __str__(self):
        return self.name


# Default Django user model is used for authentication, and this Profile model extends it with additional fields to make it suitable for student users
class Profile(models.Model):
    

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
        )

    profile_pic = models.ImageField(
        upload_to="profile_pictures/",
        blank = True,
        null = True
        )

    bio = models.TextField(
        blank=True,
        default = "I am a user without a bio yet."
        )

    YEAR_IN_SCHOOL_CHOICES = [
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
        ('PD', 'Doctoral'),
    ]

    classification = models.CharField(
        max_length=2,
        choices= YEAR_IN_SCHOOL_CHOICES,
        default='FR'
    )

    classes = models.ManyToManyField(Course, blank=True) # Stores a list of classes the student is enrolled in (They can add/remove classes from their profile)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True) # Uses SQL lite database of UTRGV Colleges and Majors. 
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, blank=True) # Drop down menu is in forms to be shown on website
    


    def __str__(self):
        return self.user.username if self.user_id else "Profile"


# This is how our backend will store our study group / events
class GroupEvent(models.Model): 
    group = models.ForeignKey(
        'StudyGroup', 
        on_delete=models.CASCADE, 
        related_name='events', 
        null=True
        ) # allows us to associate events with a specific study group

    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_events',
        null=True) # the user who created the event

    title = models.CharField(max_length=255) # title of the event
    description = models.TextField(blank=True) # description of the event
    start_time = models.DateTimeField(null=True) # when the event starts
    end_time = models.DateTimeField(null=True) # when the event ends
    location = models.CharField(max_length=255, blank=True) # where the event will take place (can be virtual or physical)

    attendees = models.ManyToManyField(
        User,
        related_name='events_attending',
        blank=True
    )

    google_event_id = models.CharField(max_length=255, blank=True) 
    google_event_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['start_time']

    def __str__(self):    
        return self.title

class FeedChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feed_messages")
    content = models.TextField(blank=True)
    resource_file = models.FileField(upload_to='feed_resources/', blank=True, null=True)
    resource_title = models.CharField(max_length=255, blank=True)
    resource_file_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.content[:30] if self.content else self.resource_title[:30]
        return f"{self.user.username}: {self.content[:30]}"

class StudyGroup(models.Model):
    COLOR_CHOICES = [
        ('#2563eb', 'Blue'),
        ('#22c55e', 'Green'),
        ('#a855f7', 'Purple'),
        ('#f97316', 'Orange'),
        ('#ef4444', 'Red'),
        ('#14b8a6', 'Teal'),
    ]

    course_code = models.CharField(max_length=20)
    course_subject = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='#2563eb')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='study_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_code} - {self.name}"

class GroupPost(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_posts')
    content = models.TextField(blank=True)
    resource_file = models.FileField(upload_to='group_resources/', blank=True, null=True)
    resource_title = models.CharField(max_length=255, blank=True)
    resource_file_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.content[:30] if self.content else self.resource_title[:30]
        return f"{self.user.username} in {self.group.name}: {self.content[:30]}"