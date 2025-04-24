from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    foxcoins = models.PositiveIntegerField(default=0, verbose_name="Foxcoins")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.username