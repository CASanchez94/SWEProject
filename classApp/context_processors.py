from .models import StudyGroup

def user_groups(request):
    if request.user.is_authenticated:
        groups = request.user.study_groups.all().order_by('name')
    else:
        groups = StudyGroup.objects.none()

    return {
        'groups': groups
    }