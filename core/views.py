from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomSignupForm, ProfileForm, UserForm
from .models import Match, VolunteerSlot, Profile

def signup(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect("match_list")
    else:
        form = CustomSignupForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile(request):
    return render(request, "core/profile.html", {"user": request.user})

@login_required
def edit_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def match_list(request):
    # ensure the user has a profile
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_team = profile.home_team

    matches = Match.objects.all().prefetch_related("slots", "home_team")

    match_data = []
    for match in matches:
        can_volunteer = True
        if user_team and match.home_team == user_team:
            can_volunteer = False

        user_signed_up = match.slots.filter(volunteer=request.user).exists()
        open_slot = match.slots.filter(volunteer__isnull=True).first()

        match_data.append({
            "match": match,
            "can_volunteer": can_volunteer,
            "user_signed_up": user_signed_up,
            "open_slot": open_slot,
        })

    return render(request, "core/match_list.html", {"match_data": match_data})

@login_required
def signup_slot(request, match_id, slot_id):
    slot = get_object_or_404(VolunteerSlot, id=slot_id, match_id=match_id)

    if slot.volunteer is not None:
        messages.error(request, "This slot is already taken.")
    elif slot.match.volunteer_count >= 3:
        messages.error(request, "This match already has 3 volunteers.")
    elif slot.match.slots.filter(volunteer=request.user).exists():
        messages.error(request, "You are already volunteering for this match.")
    else:
        slot.volunteer = request.user
        slot.save()
        messages.success(request, "You successfully signed up, thanks a lot!")

    return redirect("match_list")


