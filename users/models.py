from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
import string
import random


# Create your models here.
class Roles(models.Model):
    role_name = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return self.role_name


class users_manager(BaseUserManager):
    def create_user(self, email, phone, name, password=None):
        # if not email:
        #     raise ValueError ("Email is required")

        # if not phone:
        #     raise ValueError ("Phone Number is required")

        # if not name:
        #     raise ValueError ("Name  is required")

        user = self.model(email=self.normalize_email(email),
                          phone=phone,
                          name=name)
        # user.set_password("ipac@123456")
        user.set_password(''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=8)))
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, name, password=None):
        User.objects.create(email=self.normalize_email(email), phone=phone, user_role_id=1, name=name,
                            password=make_password(password))


class User(AbstractBaseUser):
    name = models.CharField(max_length=25, null=False, blank=False, default=True)
    email = models.EmailField(max_length=50, null=False, blank=False, unique=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    password = models.CharField(max_length=1024, null=True, blank=True)
    registered_on = models.DateTimeField(auto_now_add=True)
    emp_code = models.CharField(max_length=10, null=True, unique=True)
    user_role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    current_status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]

    objects = users_manager()

    def __str__(self):
        return self.email


class ResetPassword(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=25, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=False)