from django.shortcuts import render, redirect, render
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token, send_activation_email
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import UserForm, SigninForm, ProfileSettingsForm, UserFormEdit

def signup(request):

    '''
    Handles user registration for OWLPHA UNIVERSITY.
    Prevents already authenticated users from signing up again by redirecting to home.
    On POST request with valid data:
    - Creates a new user with inactive status (to require email verification).
    - Saves the user and stores their ID in the session (used for resending activation).
    - Sends an account activation email.
    - Renders a page instructing the user to check their email.
    On GET request, displays the registration form.
    '''

    if request.user.is_authenticated:
        # Redirect to home page if user is already logged in
        return redirect('home')

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Password is already hashed in the form
            user.is_active = False # To ensure account isn't active until email verification
            user.save()

            # Store user id in session for possible resend activation
            request.session['activation_user_id'] = user.pk

            # Send activation email
            send_activation_email(user, request)

            # Render the template that informs the user to check their email
            return render(request, "pages/activation_instructions.html", {'user': user})

    else:
        form = UserForm()

    context = {
        'form': form,
        'title': 'Join OWLPHA UNIVERSITY — Explore Free Web3 Courses & Community',
    }

    return render(request, 'pages/signup.html', context)


def signin(request):

    ''''
    Handles user sign-in using either email or username.
    If already authenticated, redirects to the home page.
    On valid form submission, attempts authentication and logs the user in.
    If authentication fails, displays an error message.
    '''

    if request.user.is_authenticated:
        # Redirect to home page if user is already logged in
        profile = request.user.profile
        return redirect(profile.get_absolute_url())

    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            # Try authenticating by username or email
            user = authenticate(request, username=identifier, password=password)

            if user:
                auth_login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(user.profile.get_absolute_url())
            else:
                messages.error(request, "Invalid credentials. Please check and try again.")

    else:
        form = SigninForm()

    context = {
        'form': form,
        'title': 'Access Your OWLPHA UNIVERSITY Account | Learn Web3 & Blockchain',
    }

    return render(request, 'pages/signin.html', context)


def logout(request):

    '''
    Logs out the current user while preserving ses sion data (if any non-auth-related data exists).
    After logout, the user is redirected to the home page.
    '''
    auth_logout(request)
    return redirect('home')


def activate_account(request, uidb64, token):
    '''
    Handles the verification process when a user clicks the account activation link sent via email.
    Decodes the user's ID from the URL, checks if the token is valid, activates the account if valid,
    and renders the appropriate success or failure response.
    '''
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Render success template
        return render(request, 'pages/activation_success.html', {'user': user})
    else:
        # Render error template for invalid activation
        return render(request, 'pages/activation_invalid.html')


def resend_activation_email(request, uidb64):

    '''
    Resends the account activation email to users who haven't completed verification.
    If the account is already active, it redirects with an info message.
    Otherwise, it sends the activation email and renders a confirmation page.
    '''

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'invalid activation link')
        return redirect(signup) 

    if user.is_active:
        messages.info(request, 'Your account is already active.')
        return redirect('signin')

    # Send the activation email again
    send_activation_email(user, request)

    # Pass the user object to the template
    return render(request, "pages/resend_activation_instructions.html", {'user': user})


def custom_google_callback(request):

    """
    Handles Google OAuth2 login callback.
    If the user cancels the login (e.g., closes Google consent), 
    it redirects to the custom sign-in page with a message.
    Otherwise, it passes control to the default allauth flow.
    """

    error = request.GET.get('error')

    if error in ['access_denied', 'cancelled']:
        # User cancelled login - redirect to the custom sign in page
        return redirect(reverse('signin') + '?auth=failed')
    
    # Otherwise, let allauth handle the rest
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView

    view = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
    return view(request)

@login_required
def user_profile_dashboard(request, username, referral_code, date_joined):
    user = request.user
    profile = user.profile

    if(
        username.lower() != user.username.lower() or referral_code != profile.referral_code or date_joined != user.date_joined.strftime('%Y-%m-%d')
    ):
        return HttpResponseForbidden('Unauthorized Access')
    
    context = {
        'user': user,
        'profile': profile,
        'title': 'Owlpha University'
    }
    return render(request, 'pages/profile_dashboard.html', context)

@login_required
def profile_settings(request):
    user = request.user
    profile = request.user.profile

    if request.method == 'POST':
        user_form = UserFormEdit(request.POST, instance=user)
        profile_form = ProfileSettingsForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid:
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(
                'user_profile_dashboard',
                username=user.username,
                referral_code=profile.referral_code,
                date_joined=user.date_joined.strftime('%Y-%m-%d')
            )
    else:
        user_form = UserFormEdit(instance=user)
        profile_form = ProfileSettingsForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Account Settings | Owlpha University'
    }
    return render(request, 'pages/profile_setting.html', context)

def home(request):
    context = {
        'title' : 'OWLPHA University | Free & Bold Web3.0 Education for All',
    }
    return render(request, 'pages/landing_page.html', context)

def testing(request):
    context = {
        'title' : 'OWLPHA University | Free & Bold Web3.0 Education for All',
    }
    return render(request, 'pages/testing.html', context)