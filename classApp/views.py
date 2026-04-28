from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm, CustomRegistrationForm, FeedChatForm, ClassEntryForm, StudyGroupForm, GroupEventForm, GroupPostForm
from .models import Profile, Major, FeedChat, College, Course, StudyGroup, GroupPost
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'POST':
        form = FeedChatForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            if post.resource_file and not post.resource_title:
                post.resource_title = post.resource_file.name.split('/')[-1]

            if post.resource_file and not post.resource_file_type:
                filename = post.resource_file.name
                if '.' in filename:
                    post.resource_file_type = filename.split('.')[-1].lower()

            post.save()
            return redirect('home')
    else:
        form = FeedChatForm()

    posts = FeedChat.objects.select_related('user').order_by('-created_at')

    return render(request, 'feed.html', {
        'form': form,
        'posts': posts
    })

@login_required
def discover(request):
    groups = StudyGroup.objects.all().order_by('-created_at')
    return render(request, 'discover.html',{
        'groups': groups
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)  # Automatically add creator as a member
            messages.success(request, "Group created successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = StudyGroupForm()

    return render(request, 'create_group.html',{
        'form': form
    })

def register(request):
    if request.method == 'POST':
        print("=" * 50)
        print("REGISTRATION POST RECEIVED")
        print("POST data:", request.POST)
        
        form = CustomRegistrationForm(request.POST)
        print("Form is_valid():", form.is_valid())
        
        if form.is_valid():
            print("Form validation PASSED")
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            print(f"User created: {user.id} - {user.username}")
            
            # Update the auto-created Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.college = form.cleaned_data['college']
            profile.major = form.cleaned_data['major']
            profile.classification = form.cleaned_data['classification']
            profile.save()
            
            print(f"Profile updated for user {user.id}")
            print(f"Redirecting to: register_step2 with user_id={user.id}")
            return redirect('register_step2', user_id=user.id)
        else:
            print("Form validation FAILED")
            print("Form errors:", form.errors)
            print("Form non-field errors:", form.non_field_errors())
            print("=" * 50)
    else:
        form = CustomRegistrationForm()
    return render(request, 'register.html', {'form': form})

def register_step2(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('register')

    profile = user.profile
    class_forms = []
    default_rows = 2

    if request.method == 'POST':
        class_count = int(request.POST.get('class_count', 0))
        classes_to_add = []
        form_valid = True

        for i in range(class_count):
            form = ClassEntryForm(request.POST, prefix=f'class_{i}')
            class_forms.append(form)

            if form.is_valid():
                subject = form.cleaned_data['subject'].strip()
                section_number = form.cleaned_data['section_number'].strip()
                if subject or section_number:
                    if not subject or not section_number:
                        form.add_error(None, 'Both subject and section number are required for each class entry.')
                        form_valid = False
                    else:
                        classes_to_add.append((subject, section_number))
            else:
                form_valid = False

        if form_valid:
            for subject, section_number in classes_to_add:
                course_name = f"{subject} {section_number}"
                course, _ = Course.objects.get_or_create(name=course_name)
                profile.classes.add(course)

            profile.save()
            messages.success(request, "Account setup complete! Welcome to Study App Name!")
            return redirect('login')
    else:
        for i in range(default_rows):
            class_forms.append(ClassEntryForm(prefix=f'class_{i}'))

    return render(request, 'register_step2.html', {
        'class_forms': class_forms,
        'user': user,
        'profile': profile
    })

# AJAX View for dynamic dropdown (Used on Registration and Profile Update pages)
def load_majors(request):
    college_id = request.GET.get('college_id')
    classification = request.GET.get('classification')
    
    # Filter majors by college
    majors = Major.objects.filter(college_id=college_id).order_by('name')
    
    # If classification is provided, filter by graduate/undergraduate
    if classification:
        is_graduate = (classification == 'GR' or classification == 'PD')
        majors = majors.filter(is_graduate=is_graduate)
    
    return render(request, 'major_dropdown_options.html', {'majors': majors})

@login_required	
def profile(request):
    # Ensure profile exists for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            print("User profile updatedd successfully")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    
    return render(request, "profile.html", {"u_form": u_form, "p_form":p_form})

@login_required
def profile_page(request):
    events = request.user.events_attending.all().order_by('date')
    return render(request, "profile_page.html", {"events": events})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)
    is_member = request.user in group.members.all()
    posts = group.posts.select_related('user').order_by('-created_at')
    resources = group.posts.filter(resource_file__isnull=False).select_related('user').order_by('-created_at')

    if request.method == 'POST':
        if not is_member:
            messages.error(request, "You must join the group before posting.")
            return redirect('group_detail', group_id=group.id)

        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.user = request.user

            if post.resource_file and not post.resource_title:
                post.resource_title = post.resource_file.name.split('/')[-1]

            if post.resource_file and not post.resource_file_type:
                filename = post.resource_file.name
                if '.' in filename:
                    post.resource_file_type = filename.split('.')[-1].lower()

            post.save()
            messages.success(request, "Post shared with the group.")
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupPostForm()
    return render(request, 'group_details.html', {
        'group': group,
        'posts': posts,
        'resources': resources,
        'form': form,
        'is_member': is_member
    })

@login_required
def join_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method == 'POST':
        group.members.add(request.user)
        messages.success(request, "You joined the group.")
    
    return redirect('group_detail', group_id=group.id)


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method == 'POST':
        if request.user == group.creator:
            messages.error(request, "The creator cannot leave their own group.")
        else:
            group.members.remove(request.user)
            messages.success(request, "You left the group.")
    
    return redirect('group_detail', group_id=group.id)

@login_required
def delete_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)

    if request.method == 'POST':
        if request.user == post.user:
            group_id = post.group.id
            post.delete()
            messages.success(request, "Post deleted.")
            return redirect('group_detail', group_id=group_id)
        else:
            messages.error(request, "You can only delete your own posts.")

    return redirect('group_detail', group_id=post.group.id)