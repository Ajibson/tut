from rest_framework import serializers
from django.conf import settings
import jwt


def validate_passwords(password, confirm_password) -> None:
    if len(password) < 8:
        raise serializers.ValidationError(
            {
                "password": "This password is too short. It must contain at least 8 characters."
            }
        )
    if password.isalpha() or password.isnumeric():
        raise serializers.ValidationError({"password": "password must be alphanumeric"})
    if confirm_password != password:
        raise serializers.ValidationError(
            {"confirm_password": "passwords do not match"}
        )
    
def decode_jwt(token) -> tuple:
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("id", None)

        if user_id is None:
            # return None, "Invalid token."
            raise jwt.InvalidTokenError("Invalid token")

        return user_id, None

    except jwt.ExpiredSignatureError:
        return None, "Invalid token."

    except jwt.InvalidTokenError as e:
        return None, "Invalid token."
