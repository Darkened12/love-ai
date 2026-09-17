from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    system_prompt = models.TextField(max_length=3000, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True)
    assistant_profile_picture = models.ImageField(upload_to="profile_pics/", null=True)