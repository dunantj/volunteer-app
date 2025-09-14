from django.contrib import admin
from .models import Match, VolunteerSlot, HomeTeam, Profile


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'home_team', 'guest_team', 'location')
    list_filter = ('date', 'location', 'home_team')
    search_fields = ('home_team__name', 'guest_team')


@admin.register(VolunteerSlot)
class VolunteerSlotAdmin(admin.ModelAdmin):
    list_display = ('match', 'volunteer')
    list_filter = ('match', 'volunteer')


@admin.register(HomeTeam)
class HomeTeamAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'home_team')
    list_filter = ('home_team',)

