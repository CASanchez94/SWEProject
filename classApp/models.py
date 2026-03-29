from django.db import models
from django.contrib.auth.models import User

class College(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Major(models.Model):

    name = models.CharField(max_length=255)
    # Allows only majors from specific college
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="majors")

    def __str__(self):
        return self.name

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

    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, blank=True)
    


    def __str__(self):
        return self.user.username if self.user_id else "Profile"


class GroupEvent(models.Model):
    title = models.CharField(max_length=200, default = "New Event")
    date = models.DateField(blank=True)
    location = models.TextField()

    # This stores the "group" in the database
    attendees = models.ManyToManyField(User, related_name="events_attending",blank = True)


    def __str__(self):
        return self.title