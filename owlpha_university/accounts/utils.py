from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates a secure token for activating user accounts.
    Includes a 3-day expiration policy based on `date_joined`.
    """

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_active}'
    
    def check_token(self, user, token):
        # Django first check for default token logic
        if not super().check_token(user, token):
            return False
        
        # Then Adds time based expiration logic (3 days)
        created_at = user.date_joined
        now = timezone.now()

        # Expire token if more than 3 days
        if (now - created_at) > timedelta(days=3):
            return False
        
        return True

account_activation_token = AccountActivationTokenGenerator()

# This function sends the account activation code via email.
def send_activation_email(user, request):
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = request.build_absolute_uri(
	    reverse('activate', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Welcome to OWLPHA University! Verify Your Account Today'

    #Render the email template with the necessary context
    message = render_to_string('pages/activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })

	# Send the email
    send_mail(
        subject,
        '',  # Empty string for plain text message (optional, since we're sending HTML)
        settings.DEFAULT_FROM_EMAIL, # Uses value from settings.py
        [user.email],
        html_message=message,  # Include the rendered HTML template as the HTML message
        fail_silently=False,
    )
