from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	class College(models.TextChoices):
		Undecided = "UNDC", "Undecided"
		CompSciAndEngr = "CSEN", "Computer Science and Engineering"
		LiberalArts = "LAC", "Liberal Arts"
		Business = "BUSI", "Business & Entrepreneurship"
		FineArts = "ARTS", "Fine Arts"
		Sciences = "SCI", "Science"

	class Major(models.TextChoices):
		Undecided = "UNDC", "Undecided"
		CompSci = "CSCI", "Computer Science"
		English = "ELA", "English"
		Finance = "FINC", "Finance"
		Art     = "ART", "Art"
		Biology = "BIO", "Biology"

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

	bio = models.TextField(blank=True)

	college = models.CharField(
		max_length = 4,
		choices = College.choices,
		default= College.Undecided,
	)
	major = models.CharField(
		max_length = 4,
		choices= Major.choices,
		default= Major.Undecided,
	)


	def __str__(self):
		return self.user.username if self.user_id else "Profile"


#class UTRGV_event(models.Model):
#	date = models.DateField(blank=True)
#	location = model.TextField()
#	cost = models.IntegerField()