from django.contrib import admin
from .models import College, Major, Profile, StudyGroup, GroupPost, FeedChat
# Register your models here.

admin.site.register(College)
admin.site.register(Major)
admin.site.register(Profile)
admin.site.register(StudyGroup)
admin.site.register(GroupPost)
admin.site.register(FeedChat)