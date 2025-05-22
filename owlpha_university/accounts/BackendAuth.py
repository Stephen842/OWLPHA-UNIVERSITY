from django.contrib.auth.backends import BaseBackend
from .models import User

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Allow User to log in with either email or username (case insensitive)."""
        if not username or not password:
            return None
            
        username = username.lower() # Ensure case insensitivity

        # Check if input is an email or username
        user = None
        if '@' in username:
            user = User.objects.filter(email=username).first() # Fetch user by email
        else:
            user = User.objects.filter(username=username).first() # Fetch user by username

        # Verify password
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None