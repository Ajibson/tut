from rest_framework import serializers
from .models import Account
from .utils import validate_passwords


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = [
            "email",
            "username",
            "password",
            "confirm_password",
            "term_and_condition",
            "address",
        ]

    def validate(self, data) -> serializers:
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        validate_passwords(password, confirm_password)
        del data["confirm_password"]

        return data
