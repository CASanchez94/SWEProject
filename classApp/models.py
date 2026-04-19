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
    title = models.CharField(max_length=200, default = "New Event") 
    description = models.TextField(blank = True, default = "This event is happening!")
    date = models.DateField(blank=True, default = date.today() + timedelta(days=7)) # Default to one week from today if no date is provided (USERS should specify tho)
    location = models.TextField() 

    # This stores the "group" in the database
    attendees = models.ManyToManyField(User, related_name="events_attending",blank = True)


    def __str__(self):
        return self.title

class FeedChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feed_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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