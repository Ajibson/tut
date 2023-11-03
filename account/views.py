from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializer import RegistrationSerializer
from .tasks import send_email_task
from django.template.loader import render_to_string
from django.shortcuts import redirect
from .utils import decode_jwt
from .models import Account
from django.conf import settings

@api_view(["POST"])
@permission_classes([AllowAny])
def RegistrationView(request) -> Response:
    with transaction.atomic():
        try:
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            # send welcome mail to user
            subject = "Ecoms Welcome Mail"
            message = ""  # this is needed to be empty although html message is to be sent
            from_email = "noreply@example.com"
            recipient_list = [instance.email]
            generated_token = instance.get_confirmation_token
            # Render the HTML template
            html_message = render_to_string(
                "welcome_mail.html",
                {"request": request, "username": instance.username, "confirm_token": generated_token},
            )
            send_email_task.delay(subject, message, from_email, recipient_list, html_message=html_message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            transaction.set_rollback(True)
            print(e)
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
@permission_classes([AllowAny])
def ConfirmRegistration(request):
    token = request.GET.get("token")
    # redirect user to page to tell them to request for new validation email
    if not token:
        return redirect(settings.CONFIRMATION_MAIL_REQUEST_PAGE)
    # get user id
    user_id, error = decode_jwt(token)
    if user_id and error is None:
        user = Account.objects.filter(id=user_id)
        if user.exists():
            user.update(verified=True)
            # TODO: redirect to homepage
            return redirect(settings.FRONTEND_HOMEPAGE)
    # TODO: redirect user to page to tell them to request for new validation email
    return redirect(settings.CONFIRMATION_MAIL_REQUEST_PAGE)