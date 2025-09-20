from django.test import TestCase
from django.contrib.auth.models import User
from .models import Match, VolunteerSlot, Profile, HomeTeam
from django.urls import reverse
from datetime import datetime, date, time

class VolunteerAppTests(TestCase):

    def setUp(self):
        # Create teams
        self.team_a = HomeTeam.objects.create(name="Team A")
        self.team_b = HomeTeam.objects.create(name="Team B")
        self.team_c = HomeTeam.objects.create(name="Team C")
        self.team_d = HomeTeam.objects.create(name="Team D")

        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Create a match
        self.match = Match.objects.create(
            date=date.today(),
            start_time=time(10, 0),
            home_team=self.team_b,
            guest_team=self.team_c,
            location="Stadium 1"
        )

        # Create slots for this match
        self.slot1 = VolunteerSlot.objects.create(match=self.match)
        self.slot2 = VolunteerSlot.objects.create(match=self.match)

    def test_signup_and_volunteer(self):
        # Login the user
        login = self.client.login(username="testuser", password="testpass")
        self.assertTrue(login)

        # Check match list view
        response = self.client.get(reverse("match_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team B vs Team C")

        # Sign up for first slot
        response = self.client.get(reverse("signup_slot", args=[self.match.id, self.slot1.id]))
        self.assertRedirects(response, reverse("match_list"))

        # Refresh from DB
        self.slot1.refresh_from_db()
        self.assertEqual(self.slot1.volunteer, self.user)

    def test_home_team_filter(self):
        # Create a second match with a different home team
        match2 = Match.objects.create(
            date=date.today(),
            start_time=time(14, 0),
            home_team=self.team_a,
            guest_team=self.team_d,
            location="Stadium 2"
        )

        # Create slots for second match
        VolunteerSlot.objects.create(match=match2)
        VolunteerSlot.objects.create(match=match2)

        # Login
        self.client.login(username="testuser", password="testpass")

        # 1️⃣ Request match list without filter - should contain both matches
        response = self.client.get(reverse("match_list"))
        self.assertContains(response, f"{self.team_b} vs {self.team_c}")
        self.assertContains(response, f"{self.team_a} vs {self.team_d}")

        # 2️⃣ Filter by Team B - should show only the first match
        response = self.client.get(reverse("match_list") + f"?team={self.team_b.name}")
        self.assertContains(response, f"{self.team_b} vs {self.team_c}")
        self.assertNotContains(response, f"{self.team_a} vs {self.team_d}")

        # 3️⃣ Filter by Team A - should show only the second match
        response = self.client.get(reverse("match_list") + f"?team={self.team_a.name}")
        self.assertNotContains(response, f"{self.team_b} vs {self.team_c}")
        self.assertContains(response, f"{self.team_a} vs {self.team_d}")

    def test_delete_user_and_match(self):
        # Delete user
        self.user.delete()
        self.assertFalse(User.objects.filter(username="testuser").exists())
        
        # The slot should no longer have a volunteer
        self.slot1.refresh_from_db()
        self.assertIsNone(self.slot1.volunteer)

        # Delete match
        match_id = self.match.id
        self.match.delete()
        self.assertFalse(Match.objects.filter(id=match_id).exists())
        self.assertFalse(VolunteerSlot.objects.filter(match_id=match_id).exists())

