from django.db import models
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
        
class Customer(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+[1-9]\d{1,14}$', 'Invalid phone format')]
        )
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
        if self.phone and not self.phone.isdigit():
            raise ValidationError("Phone number must contain only digits.") 
        if self.name:
            self.name = self.name.strip()
    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean method to validate and normalize data
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({self.code}) - {self.phone or 'No phone'}"
    
