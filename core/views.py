from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .forms import CustomSignupForm, ProfileForm, UserForm, OfferForm
from .models import Match, VolunteerSlot, Profile, Offer

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

    # --- filtering logic ---
    selected_team = request.GET.get("team")
    only_my_matches = request.GET.get("my_matches") == "on"
    matches = (
        Match.objects.all()
        .prefetch_related("slots", "home_team")
        .order_by("date")  # upcoming matches first
    )
    if selected_team:
        matches = matches.filter(home_team__name=selected_team)
    if only_my_matches:
        matches = matches.filter(slots__volunteer=request.user).distinct()

    # collect all home teams for dropdown
    teams = Match.objects.values_list("home_team__name", flat=True).distinct()

    match_data = []
    for match in matches:
        can_volunteer = not (user_team and match.home_team == user_team)
        user_signed_up = match.slots.filter(volunteer=request.user).exists()
        open_slot = match.slots.filter(volunteer__isnull=True).first()

        match_data.append({
            "match": match,
            "can_volunteer": can_volunteer,
            "user_signed_up": user_signed_up,
            "open_slot": open_slot,
        })

    return render(
        request,
        "core/match_list.html",
        {
            "match_data": match_data,
            "teams": teams,
            "selected_team": selected_team,
            "only_my_matches": only_my_matches,
        },
    )

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

class OfferListView(ListView):
    model = Offer
    template_name = "offer_list.html"
    context_object_name = "offers"
    queryset = Offer.objects.order_by("-created_at")

    def get_queryset(self):
        queryset = Offer.objects.all().order_by("-created_at")
        status = self.request.GET.get("status", "open")
        my_offers = self.request.GET.get("my_offers") == "on"

        if status != "all":
            queryset = queryset.filter(status=status)
        if my_offers and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_status"] = self.request.GET.get("status", "open")
        context["my_offers"] = self.request.GET.get("my_offers") == "on"
        return context

class OfferCreateView(CreateView):
    model = Offer
    form_class = OfferForm
    template_name = "core/offer_creation_form.html"
    success_url = reverse_lazy("offer_list")

    def get_initial(self):
        initial = super().get_initial()
        slot_id = self.request.GET.get("slot")
        offer_type = self.request.GET.get("type")
        if slot_id:
            initial["slot"] = slot_id
        if offer_type:
            initial["type"] = offer_type
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
@login_required
def accept_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id, status="open")
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    user_team = profile.home_team
    user_slots = VolunteerSlot.objects.filter(
        match=offer.slot.match, volunteer=user
    )

    if offer.type == "trade":
        if user_team and (offer.slot.match.home_team == user_team or offer.slot.match.guest_team == user_team):
            messages.error(request, "Can't accept, you are playing!")
            return redirect("offer_list")
        if user_slots.exists():
            messages.error(request, "You already volunteer for this match.")
            return redirect("offer_list")
        else:
            # Swap volunteers between slots
            offerer_slot = offer.slot
            offerer_slot.volunteer = user
            offerer_slot.save()

    elif offer.type == "time":
        if not user_slots.exists():
            messages.error(request, "You must have a slot in this match to accept the offer.")
            return redirect("offer_list")
        else:
            # Accepter takes the slot, offerer slot becomes open
            offer.slot.volunteer = user
            offer.slot.save()

    offer.status = "closed"
    offer.save()
    messages.success(request, "Offer accepted and slots updated.")
    return redirect("offer_list")
