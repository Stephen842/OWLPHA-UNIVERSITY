from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
from django.utils import timezone
from courses.models import Course, Badge, Interest


# Create your models here.

'''This is for my Custom User model '''
class UsersManager(BaseUserManager):
    def create_user(self, email, name, username, country, password=None):
        if not email:
            raise ValueError('Enter Email address')
        if not name:
            raise ValueError('Enter Full name')
        if not username:
            raise ValueError('Enter Username')
        if not country:
            raise ValueError('Enter Country')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            username=username,
            country=country,
        )
        user.set_password(password)  # Hash the password
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, username, country, password=None):
        user = self.create_user(
            email=email,
            name=name,
            username=username,
            country=country,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True

        if user.is_staff is not True:
            raise ValueError('Superuser must have is_staff=True')
        if user.is_superuser is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):  # Add PermissionsMixin here
    name = models.CharField(max_length=50, blank=False)
    username = models.CharField(max_length=50, unique=True, blank=False)
    email = models.EmailField(unique=True, blank=False)
    country = CountryField(blank=False, blank_label='Select Country',)
    date_joined = models.DateTimeField(default=timezone.now)
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, blank=True, null=True)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username', 'country']

    def save(self, *args, **kwargs):
        """Ensure username and email are stored in lowercase"""
        self.email = self.email.lower()
        self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_name(self):
        """Return the user's full name"""
        return self.name

    def get_short_name(self):
        """Return the short name (username in this case)"""
        return self.username
    
    class Meta:
        verbose_name_plural = 'My User'

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    # User Basic Info
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True, region='NG')
    gender = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ]
    )
    date_of_birth = models.DateField(blank=True, null=True)

    # User Socials & Interests
    interests = models.ManyToManyField(Interest, blank=True)
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    discord_handle  = models.CharField(max_length=50, blank=True, null=True)

    # User Learning Goals & Progress
    learning_goals = models.TimeField(blank=True, null=True)
    current_courses = models.ManyToManyField(Course, related_name='active_learners', blank=True)
    completed_course = models.ManyToManyField(Course, related_name='graduates', blank=True)
    course_progress = models.JSONField(default=dict)

    # Gamification
    xp_points = models.IntegerField(default=20)
    badges = models.ManyToManyField(Badge, blank=True)

    # User Web3 wallet
    wallet_address = models.CharField(max_length=255, blank=True, null=True)

    # User Referral Code
    referral_code = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def generate_referral_url(self):
        current_site = Site.objects.get_current()
        domain = current_site.domain
        return f'https://{domain}/signup?ref={self.referral_code}'
    
    def get_absolute_url(self):
        return reverse(
            'user_profile_dashboard',
            kwargs={
                'username': self.user.username,
                'referral_code': self.referral_code,
                'date_joined': self.user.date_joined.strftime('%Y-%m-%d')
            }
        )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    # User roles
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')