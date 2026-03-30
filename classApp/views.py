from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm 
from .forms import UserUpdateForm, ProfileUpdateForm, CustomRegistrationForm
from .models import Profile, Major
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# @login_required
def home(request):
	return render(request, 'feed.html',{})
@login_required
def discover(request):
	return render(request, 'discover.html',{})
@login_required
def create_group(request):
	return render(request, 'create_group.html',{})

def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Update the auto-created Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.college = form.cleaned_data['college']
            profile.major = form.cleaned_data['major']
            profile.save()
            
            return redirect('login')
    else:
        form = CustomRegistrationForm()
    return render(request, 'register.html', {'form': form})

# AJAX View for dynamic dropdown
def load_majors(request):
    college_id = request.GET.get('college_id')
    majors = Major.objects.filter(college_id=college_id).order_by('name')
    return render(request, 'major_dropdown_options.html', {'majors': majors})

@login_required	
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            print("User profile udpated successfully")
            return redirect("home")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, "profile.html", {"u_form": u_form, "p_form":p_form})

@login_required
def profile_page(request):
    events = request.user.events_attending.all().order_by('date')
    return render(request, "profile_page.html", {"events": events})