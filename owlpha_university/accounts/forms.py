from django import forms
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.forms.widgets import TextInput
from .models import Users

class UserForm(forms.ModelForm):
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

    country = CountryField(blank_label='Select Country').formfield(
        widget=CountrySelectWidget(),
        required=True
    )

    class Meta:
        model = Users
        fields = ['name', 'username', 'email', 'country', 'password1', 'password2']


    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:
            raise forms.ValidationError('Name must be 8 characters long or more')
        return name
    
    def clean_username(self):
        username = self.cleaned_data.get('username').lower()  # Convert to lowercase
        if Users.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower() # Convert to lowercase
        if len(email) < 8:
            raise forms.ValidationError('Email address must be 8 characters long')
        if Users.objects.filter(email=email).exists():
            raise forms.ValidationError('Email Address Already Registered...')
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
        if not any(char in "!@#$%^&*()-_=+" for char in password):
            hint_messages.append("Include at least one special character (!@#$%^&*()-_=+).")

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
    identifier = forms.CharField(label="Email or Username")
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_identifier(self):
        """Ensure identifier (username or email) is stored in lowercase."""
        identifier = self.cleaned_data.get('identifier')
        if identifier:
            return identifier.lower()  # Convert to lowercase for case insensitivity
        return identifier