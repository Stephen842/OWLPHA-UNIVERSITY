from django import forms
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.utils import timezone
from datetime import timedelta
from .models import User, UserProfile

class UserForm(forms.ModelForm):
    """
    User signup form.
    
    Includes:
    - Name, Username, Email, Country fields.
    - Password fields with validation.
    """
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'country']
        widgets = {
            'country': CountrySelectWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].required = True
        self.fields['country'].widget.attrs.update({'data-placeholder': 'Select Country'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 6:
            raise forms.ValidationError('Name must be 6 characters long or more')
        return name
    
    def clean_username(self):
        username = self.cleaned_data.get('username').lower()  # Convert to lowercase
    
        try:
            existing_user = User.objects.get(username=username)

            # If user exists and is inactive + older than 3 days, delete them
            if not existing_user.is_active:
                if timezone.now() - existing_user.date_joined > timedelta(days=3):
                    existing_user.delete()
                    return username
                else:
                    raise forms.ValidationError('This username is registered but not yet activated. Please check your inbox or try resending the activation link.')
            else:
                raise forms.ValidationError('Username already taken.')
            
        except User.DoesNotExist:
            return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower() # Convert to lowercase
        if len(email) < 8:
            raise forms.ValidationError('Email address must be 8 characters long')
        
        try:
            existing_user = User.objects.get(email=email)

            # If user exists and is inactive + older than 3 days, delete them
            if not existing_user.is_active:
                if timezone.now() - existing_user.date_joined > timedelta(days=3):
                    existing_user.delete()
                    return email
                else:
                    raise forms.ValidationError('This email is registered but not yet activated. Please check your inbox or try resending the activation link.')
            else:
                raise forms.ValidationError('Email Address Already Registered...')
            
        except User.DoesNotExist:
            return email
   
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        hint_messages = []

        if not password:
            raise forms.ValidationError("Password is required.")

        # Check for uppercase letter
        if not any(char.isupper() for char in password):
            hint_messages.append("Include at least one uppercase letter.")

        # Check for a number
        if not any(char.isdigit() for char in password):
            hint_messages.append("Include at least one number.")

        # Check for a special character
        if not any(char in "!@#$%^&*()-_=+~{[}]?/;:," for char in password):
            hint_messages.append("Include at least one special character (!@#$%^&*()-_=+~{[}]?/;:,).")

        # If there are any hints, return a combined message instead of raising an error immediately
        if hint_messages:
            raise forms.ValidationError("\n".join(hint_messages))

        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1']) # Hash password
        if commit:
            user.save()
        return user

    
class SigninForm(forms.Form):
    """
    Basic sign-in form.

    Accepts username or email as identifier.
    """
    identifier = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_identifier(self):
        """Ensure identifier (username or email) is stored in lowercase."""
        identifier = self.cleaned_data.get('identifier')
        if identifier:
            return identifier.lower()  # Convert to lowercase for case insensitivity
        return identifier

class UserFormEdit(forms.ModelForm):
    """
    User profile update form.

    Includes:
    - Editable name, username, country.
    - Editable `new_email` prefilled with current email.
    """
    new_email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ['name', 'username', 'country', 'new_email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill the field with the current user email if instance exists
        if self.instance and self.instance.pk:
            self.fields['new_email'].initial = self.instance.email

    def save(self, commit=True):
        user = super().save(commit=False)

        new_email = self.cleaned_data.get('new_email')

        # Make sure to compare to the current user.email
        if new_email and new_email != user.email:
            user.new_email = new_email
        else:
            # CLEAR new_email if same or empty
            user.new_email = None

        if commit:
            user.save()
        return user

class ProfileSettingsForm(forms.ModelForm):
    """
    Profile settings form.

    Includes bio, profile image, contact, links, interests, wallet, etc.
    """
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'profile_image', 'phone_number', 'gender', 'date_of_birth',
            'github_link', 'linkedin_link', 'twitter_link', 'learning_goals',
            'wallet_address', 'interests'
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if len(bio) > 260:
            raise forms.ValidationError('Bio must be 150 Characters or fewer.')
        return bio