from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HomeTeam, Profile, Offer, VolunteerSlot

# --- SIGNUP FORM ---
class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    home_team = forms.ModelChoiceField(
        queryset=HomeTeam.objects.all(),
        required=False,
        empty_label="No home team"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password1",
            "password2",
            "home_team",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            # Save profile fields
            profile = user.profile
            profile.phone_number = self.cleaned_data.get("phone_number", "")
            home_team = self.cleaned_data.get("home_team")
            if home_team:
                profile.home_team = home_team
            profile.save()
        return user


# --- USER EDIT FORM ---
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# --- PROFILE EDIT FORM ---
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'home_team']

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["type", "slot", "details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["slot"].queryset = VolunteerSlot.objects.filter(volunteer=user)