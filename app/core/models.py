from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)


class UserManager(BaseUserManager):
    """Manager for User objects."""

    def create_user(self, email, password=None, **kwargs):
        """Create, save and return new User object."""

        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **kwargs,)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        "Create and return a new superuser."

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User object used in system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
