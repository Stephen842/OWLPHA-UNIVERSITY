from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from .models import User, UserProfile

def generate_unique_referral_code():
    while True:
        code = str(uuid.uuid4())[:8]
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        referral_code = generate_unique_referral_code()
        UserProfile.objects.create(user=instance, referral_code=referral_code)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

