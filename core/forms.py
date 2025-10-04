from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HomeTeam, Profile, Offer, VolunteerSlot

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    home_team = forms.ModelChoiceField(
        queryset=HomeTeam.objects.all(),
        required=False,
        empty_label="No home team"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "home_team")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Save home_team into profile
            home_team = self.cleaned_data.get("home_team")
            if home_team:
                user.profile.home_team = home_team
                user.profile.save()
        return user

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            # Save phone number to profile
            user.profile.phone_number = self.cleaned_data["phone_number"]
            user.profile.save()
        return user

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Profile
        fields = ("phone_number", "home_team")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile.save()
        return profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # let user edit these

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