from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User

class Command(BaseCommand):
    help = "Delete users who haven't activated their account within 3 days"

    def handle(self, *args, **kwargs):
        threshold_date = timezone.now() - timedelta(days=3)

        # Filter users who are inactive and joined more than 3 days ago
        expired_users = User.objects.filter(is_active=False, date_joined__lt=threshold_date)
        count = expired_users.count()

        if count > 0:
            self.stdout.write(f'Deleting {count} expired user(s)...')
            expired_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired account(s).'))

        else:
            self.stdout.write('No expired user found.')