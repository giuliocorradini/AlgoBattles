from django.contrib.auth.models import User, AbstractUser
from django.db import models
from AlgoBattles import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github = models.CharField(max_length=100, default="")
    linkedin = models.CharField(max_length=255, default="")
    picture = models.ImageField(upload_to="propics")
