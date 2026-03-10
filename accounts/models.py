from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_active_plan(self):
        try:
            user_plan = self.user_plan
        except Exception:
            return False
        return user_plan.status == "ACTIVE"

    def __str__(self):
        return self.email

