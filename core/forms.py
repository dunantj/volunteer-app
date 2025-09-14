from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import HomeTeam, Profile

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['home_team']  # add other profile fields if needed

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']  # let user edit these