# Create your models here.

from django.db import models

class SMSNotification(models.Model):
    order_id = models.PositiveIntegerField()
    to = models.CharField(max_length=32)
    message = models.TextField()
    status = models.CharField(max_length=32, choices=[("pending","pending"),("sent","sent"),("failed","failed")], default="pending")
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SMS for order {self.order_id} -> {self.to} ({self.status})"
