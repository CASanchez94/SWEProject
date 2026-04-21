from django.contrib import admin
from .models import College, Major, Profile, StudyGroup
# Register your models here.

admin.site.register(College)
admin.site.register(Major)
admin.site.register(Profile)
admin.site.register(StudyGroup)