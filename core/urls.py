# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.match_list, name="match_list"),
    path("signup-slot/<int:match_id>/<int:slot_id>/", views.signup_slot, name="signup_slot"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
