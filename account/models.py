from django.db import models
from django.contrib.auth.models import AbstractUser
import jwt
from django.conf import settings
from django.utils import timezone
import secrets
import string
from datetime import timedelta

class Account(AbstractUser):
    username = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=300, unique=True)
    verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    image = models.ImageField(upload_to='account/profile', blank=True)
    created_from = models.CharField(max_length=15)
    term_and_condition = models.BooleanField(default=False)
    updated_at = models.DateField(auto_now=True)

    USERNAME_FIELD = 'email' # this will be used to log in users instead of username
    REQUIRED_FIELDS = ['username'] # this is for admin when creating superuser


    @property
    def get_confirmation_token(self):
        return self.generate_password_reset_account_validation_token()

    def generate_password_reset_account_validation_token(self):
        values = string.ascii_letters + string.digits
        token = "".join(secrets.choice(values) for _ in range(250))
        dt = timezone.now() + timedelta(seconds=settings.CONFIRMATION_LINK_TIMEOUT)
        encode_token = jwt.encode(
            {"token": token, "exp": int(dt.strftime("%s")), "id": self.id},
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return encode_token

class FailedEmailTasks(models.Model):
    task_id = models.CharField(max_length=255)
    exc = models.TextField()
    args = models.JSONField()
    kwargs = models.JSONField()
    einfo = models.TextField()