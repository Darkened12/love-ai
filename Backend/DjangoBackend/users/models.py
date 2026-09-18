from pathlib import Path

from django.db import models
from django.contrib.auth.models import AbstractUser


def read_system_prompt() -> str:
    path = Path(__file__).parent / "system_prompt.md"

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


class User(AbstractUser):
    system_prompt = models.TextField(max_length=3000, null=False, default=read_system_prompt)
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True)
    assistant_profile_picture = models.ImageField(upload_to="profile_pics/", null=True)