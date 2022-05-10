from pickle import TRUE
from django.db import models
from django.contrib.auth.models import User

class ExtendUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ver_code = models.TextField()
    
    def __str__(self):
        return self.ver_code
    