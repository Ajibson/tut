import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Account

import jwt
from django.conf import settings
from django.utils import timezone

@pytest.fixture
def api_client(db):
    return APIClient()


@pytest.fixture
def sample_user_data(db):
    return {'email': 'tut@mail.com', 'password': "tutad1234"}


@pytest.fixture
def create_sample_user():
    def create(**kwargs):
        return Account.objects.create(**kwargs)

    return create



def test_registration_pass(api_client, sample_user_data):
    sample_user_data.update({'confirm_password': sample_user_data['password']})
    registration_url = reverse('register')
    response = api_client.post(registration_url, data=sample_user_data)
    print(response.json())
    assert response.status_code == 201
    assert not Account.objects.get(email=sample_user_data['email']).verified


@pytest.mark.parametrize(
    "email, password, confirm_password, expected_status, expected_error_key, expected_message",
    [
        (
            "not-an-email","Password123","Password123",
            status.HTTP_400_BAD_REQUEST,"email","Enter a valid email address.",
        ), 
        (
            "existing@email.com","Password123","Password123",
            status.HTTP_400_BAD_REQUEST,"email","user with this email already exists.",
        ),
        (
            "valid@email.com","short","short",
            status.HTTP_400_BAD_REQUEST,"password","This password is too short. It must contain at least 8 characters.",
        ),
        (
            "valid@email.com","NoNumbers","NoNumbers",
            status.HTTP_400_BAD_REQUEST,"password","password must be alphanumeric",
        ),
        (
            "valid@email.com","NoNumbers5","NoNumbers3",
            status.HTTP_400_BAD_REQUEST,"confirm_password","passwords do not match",
        ),
    ],
)
def test_resister_user_fail(api_client,create_sample_user, sample_user_data,email,password,confirm_password,expected_status,expected_error_key,expected_message):
    register_url = reverse("register")  # get the registration URL
    if email == "existing@email.com":
        # create an existing user
        create_sample_user(
            email="existing@email.com",
            password="Password123",
        )
    sample_user_data.update(
        {"email": email, "password": password, "confirm_password": confirm_password}
    )
    response = api_client.post(register_url, data=sample_user_data)
    assert response.status_code == expected_status  # confirm status code
    assert (
        expected_message in response.json()[expected_error_key]
    )  # confirm error message


def test_confirm_registration_pass(api_client, create_sample_user, sample_user_data):
    confirm_registration_url = reverse("confirm_registration")
    sample_user_data.update(
        {"id": 9, "email": "tuttest1@ecoms.com", "password": "ecoms_1029"}
    )
    new_user = create_sample_user(**sample_user_data)
    token = new_user.get_confirmation_token
    response = api_client.get(f"{confirm_registration_url}?token={token}")

    assert response.status_code == 302
    assert Account.objects.get(email="tuttest1@ecoms.com").verified


def test_confirm_registration_fail(api_client, create_sample_user, sample_user_data):
    confirm_registration_url = reverse("confirm_registration")
    sample_user_data.update(
        {"id": 9, "email": "tuttest1@ecoms.com", "password": "ecoms_1029"}
    )
    new_user = create_sample_user(**sample_user_data)
    response = api_client.get(f"{confirm_registration_url}")

    assert response.status_code == 302
    assert not Account.objects.get(email="tuttest1@ecoms.com").verified

    # test for expired token
    token = new_user.get_confirmation_token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    payload["exp"] = int(timezone.now().strftime("%s"))
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    response = api_client.get(f"{confirm_registration_url}?token={token}")
    assert response.status_code == 302
    assert not Account.objects.get(email="tuttest1@ecoms.com").verified