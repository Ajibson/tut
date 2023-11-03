from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.RegistrationView, name="register"),
    path("confirm-registration/", views.ConfirmRegistration, name="confirm_registration"),
]
