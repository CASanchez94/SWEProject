from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm, CustomRegistrationForm, FeedChatForm, ClassesForm, StudyGroupForm
from .models import Profile, Major, FeedChat, College, StudyGroup
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'POST':
        form = FeedChatForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
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
    
    if request.method == 'POST':
        form = ClassesForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Account setup complete! Welcome to Study App Name!")
            return redirect('login')
    else:
        form = ClassesForm(instance=profile)
    
    return render(request, 'register_step2.html', {
        'form': form,
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
    return render(request, 'group_details.html', {
        'group': group
    })