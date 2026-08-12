from django.db import models
from django.contrib.auth.models import User
import os
from django.contrib.auth.models import AbstractUser

from core_APP.mixins import *


class User(
    TimestampMixin,
    SoftDeleteMixin,
    UserTrackingMixin,
    AbstractUser,
):
    """
    Custom user model for Big-MT.

    Extends Django's AbstractUser while adding:
    - TimestampMixin: created/updated timestamps
    - SoftDeleteMixin: soft deletion
    - UserTrackingMixin: created_by/updated_by tracking
    """

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.get_username()