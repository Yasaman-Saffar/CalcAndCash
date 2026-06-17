from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.utils.translation import gettext_lazy as _ 

class CustomBaseUserManager(BaseUserManager):
    def create_user(self, phone, password, **extrafields):
        if not phone:
            raise ValueError('Phone number is required.')
        if not password:
            raise ValueError('Password is required.')
        user = self.model(phone=phone, **extrafields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password, **extrafields):
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extrafields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(unique=True, max_length=20)
    phone_history = models.JSONField(default=dict, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    
    email = models.EmailField(max_length=254, null=True, blank=True)
    
    is_staff = models.BooleanField(default=False)
    
    objects = CustomBaseUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    @property
    def has_profile(self):
        return hasattr(self, "profile")
    
    
    
class Gender(models.TextChoices):
    MALE = 'male', 'Male'
    FEMAIL = 'female', 'Female'
    UNSPECIFIED = 'unspecified', 'Unspecified'

class Profile(models.Model):    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    profile_username = models.CharField(max_length=30, unique=True, blank=False, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=False)
    last_name = models.CharField(max_length=50, null=True, blank=False)
    national_id = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('National Id'))
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=Gender, default='unspecified')
    
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='profile/', null=True, blank=True)
    
    def __str__(self):
        return self.user.phone if not self.profile_username else self.profile_username
    
    @property
    def group(self):
        membership = getattr(self, "memberships", None)
        return membership.group if membership else None
 