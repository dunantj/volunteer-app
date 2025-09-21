# core/urls.py
from django.urls import path
from . import views
from .views import OfferListView, OfferCreateView

urlpatterns = [
    path("", views.match_list, name="match_list"),
    path("signup-slot/<int:match_id>/<int:slot_id>/", views.signup_slot, name="signup_slot"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("trading/", OfferListView.as_view(), name="offer_list"),
    path("trading/new/", OfferCreateView.as_view(), name="offer_create"),
    path("trading/accept/<int:offer_id>/", views.accept_offer, name="accept_offer"),
]
