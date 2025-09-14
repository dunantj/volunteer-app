from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class HomeTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
# extend User with profile info
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_team = models.ForeignKey(HomeTeam, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Match(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    home_team = models.ForeignKey(
        HomeTeam,
        on_delete=models.CASCADE,
        related_name="home_matches",
        default=1 # default to "SMZ1"
    )
    guest_team = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.date} {self.start_time.strftime('%H:%M')} – {self.home_team} vs {self.guest_team}"

    @property
    def volunteer_count(self):
        return self.slots.filter(volunteer__isnull=False).count()

    def required_slots(self):
        return self.slots.count()
    
    def create_slots(self, num=3):
        for _ in range(num - self.slots.count()):
            VolunteerSlot.objects.create(match=self)



class VolunteerSlot(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="slots")
    volunteer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="volunteer_slots"
    )

    def __str__(self):
        if self.volunteer:
            return f"{self.match} – {self.volunteer.username}"
        return f"{self.match} – (open slot)"

# Signal to create 3 empty slots whenever a match is created
@receiver(post_save, sender=Match)
def create_slots_for_match(sender, instance, created, **kwargs):
    if created:
        for _ in range(3):
            VolunteerSlot.objects.create(match=instance)