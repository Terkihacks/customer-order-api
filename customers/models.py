from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Create your models here.
class CustomerManager(models.Manager):
    def get_cust_by_code(self, code):
        return self.get(code=code.upper())
    def active_customers(self):
        #Get customers with at least one order in last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)
        return self.filter(order__created_at__gte=six_months_ago).distinct()

class CustomerManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password, **extra_fields)
        
class Customer(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(
            r'^\+[1-9]\d{1,14}$',
            'Phone number must be in international format, e.g. +254712345678'
        )]
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomerManager()

    # Indexing for faster lookups
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        managed = False 
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['phone']),
        ]
    # Model-level validation before saving to DB
    def clean(self):       
        if self.code:
            self.code = self.code.upper().strip()
        if self.name:
            self.name = self.name.strip()
    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean method to validate and normalize data
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.phone or 'No phone'}"
    
